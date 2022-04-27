import glob
import os
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

munge_dir = '/data/scripts/l2munger-main'
py3_path = '/home/tjt/anaconda3/bin/python'
base_destination_directory = '/home/tjt/public_html/public/radar/'


class Munger():
    """

    """
    
    def __init__(self,new_rda='KGRR', munge_data=True, remove_uncompressed=True, start_simulation=True):
        self.new_rda = new_rda
        self.munge_data = munge_data
        self.remove_uncompressed = remove_uncompressed
        self.start_simulation = start_simulation
        self.source_directory = Path(munge_dir)
        self.source_files = list(self.source_directory.glob('*V06'))
        self.first_file = self.source_files[0].parts[-1]
        first_file_rda = self.first_file[:4]
        if self.new_rda == 'None':
            self.new_rda = first_file_rda
        self.radar_dir = f'{base_destination_directory}{self.new_rda}'
        if self.munge_data:
            self.clean_directories();
            if self.remove_uncompressed:
                self.uncompress_files();
            self.uncompressed_files = list(self.source_directory.glob('*uncompressed'))
            self.first_file_epoch_time = self.get_timestamp(self.first_file)
            self.munge_files()
        if self.start_simulation:
            print(' Starting simulation!! \n Set polling to https://turnageweather.us/public/radar')
            self.simulation_files_directory = Path(self.radar_dir)
            self.simulation_files = sorted(list(self.simulation_files_directory.glob('*gz')))        
            self.update_dirlist()
        if not self.munge_data and not self.start_simulation:
            print('nothing to do!')
    
    def clean_directories(self):
        """
        filetype example - f'{self.new_rda}*'
        """
        os.chdir(munge_dir)
        if self.remove_uncompressed:
            uncompressed_files = glob.glob(os.path.join(munge_dir, '*.uncompressed'))
            [os.remove(f) for f in uncompressed_files]
        
        #[os.remove(f) for f in os.listdir() if f.startswith(self.new_rda)]
        os.chdir(self.radar_dir)
        [os.remove(f) for f in os.listdir()]
        return
    
    def uncompress_files(self):
        #python debz.py KBRO20170825_195747_V06 KBRO20170825_195747_V06.uncompressed
        os.chdir(munge_dir)
        for original_file in self.source_files:
            command_string = f'{py3_path} debz.py {str(original_file)} {str(original_file)}.uncompressed'
            os.system(command_string)
        print("uncompress complete!")
        return

    def get_timestamp(self,file):
        """
        Takes a filename and converts its datetime info to a timestamp (epoch seconds)
        """
        file_epoch_time = datetime.strptime(file[4:19], '%Y%m%d_%H%M%S').timestamp()
        return file_epoch_time        
    
    def munge_files(self):
        """
        Sets times of files to reference time
        """
        os.chdir(munge_dir)
        simulation_start_time = datetime.utcnow() - timedelta(seconds=(60*60*3))
        simulation_start_time_epoch = simulation_start_time.timestamp()
        for uncompressed_file in self.uncompressed_files:
            fn = str(uncompressed_file.parts[-1])
            fn_epoch_time = self.get_timestamp(fn)
            fn_time_shift = int(fn_epoch_time - self.first_file_epoch_time)
            new_time_obj = simulation_start_time + timedelta(seconds=fn_time_shift)
            new_time_str = datetime.strftime(new_time_obj, '%Y/%m/%d %H:%M:%S')
            new_filename_date_string = datetime.strftime(new_time_obj, '%Y%m%d_%H%M%S')
            command_line = f'./l2munger {self.new_rda} {new_time_str} 1 {fn}'
            print(command_line)
            print(f'     source file = {fn}')
            os.system(command_line)
            new_filename = f'{self.new_rda}{new_filename_date_string}'
            move_command = f'mv {munge_dir}/{new_filename} {self.radar_dir}/{new_filename}'
            print(move_command)
            os.system(move_command)
        
        simulation_directory = Path(self.radar_dir)
        simulation_files = list(simulation_directory.glob('*'))
        os.chdir(self.radar_dir)
        for file in simulation_files:
            print(f'compressing munged file ... {file.parts[-1]}')
            gzip_command = f'gzip {file.parts[-1]}'
            os.system(gzip_command)

        return
        
    def update_dirlist(self):
        simulation_counter = self.get_timestamp(self.simulation_files[0].parts[-1]) + 360
        last_file_timestamp = self.get_timestamp(self.simulation_files[-1].parts[-1])
        print(simulation_counter,last_file_timestamp-simulation_counter)
        while simulation_counter < last_file_timestamp:
            simulation_counter += 60
            self.output = ''            
            for file in self.simulation_files:
                file_timestamp = self.get_timestamp(file.parts[-1])
                if file_timestamp < simulation_counter:
                    line = f'{file.stat().st_size} {file.parts[-1]}\n'
                    self.output = self.output + line
                    f = open(f'{self.radar_dir}/dir.list',mode='w')
                    f.write(self.output)
                    f.close()
                else:
                    pass

            sleep(10)

        print("simulation complete!")

        return

#-------------------------------

test = Munger(new_rda='KSHV',munge_data=True,remove_uncompressed=False,start_simulation=True)

