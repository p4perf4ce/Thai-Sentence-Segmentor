import ffmpeg
import subprocess as sp
import argparse as ap


class sourceprocess:

    def __init__(self):
        # Default Configuration
        self.ac = 1
        self.ar = 44100
        self.encoding = 'wav'
        self.segt = 50
        self.overlap = 1.25
        self.wricom = False
        self.default_output_path = './output/'

    def paramsparser(self, **kwargs):
        """
        Parse Command Argument to Local Attribute and Configuration.
        Params:
        ac (int): audio channels (Default: 1 chaanel)
        ar (int): audio sample rate (Default: 44100 Hz)
        encoding (string): audio encoding (Default:Linear16 pcm_s16le as wav)
        segt (float): Time per each segment (Default: 30 seconds)
        overlap (float): Overlap time of each segment (Default: 1 second)
        wricom (boolean): Write to Disk (Default: False)
        """

        for param, value in kwargs.items():
            print('[SOURCEPROCESS] {} set as {}'.format(param, value))
            if param == 'ac':
                self.ac = value
            if param == 'ar':
                self.ar = kwargs['ar']
            if param == 'encoding':
                self.encoding = kwargs['encoding']
            if param == 'segt':
                self.segt = kwargs['segt']
            if param == 'overlap':
                self.overlap = kwargs['overlap']
            if param == 'writedisk':
                self.wricom = kwargs['writedisk']

    def writetodisk(self, audio, path):

        print('[SOURCEPROCESS][W2D] Writing Audio to {}'.format(path))
        process = (
            ffmpeg
            .input('pipe:', format='s16le')
            .output(path, format='s16le', acodec='pcm_s16le', ac=1, ar='44.1k')
            .run_async(pipe_stdin=True)
        )
        process.communicate(input=audio)

    def extract(self, source, output_path=None):
        
        print('[SOURCEPROCESS] Begin Extraction')
        print('[SOURCEPROCESS] Write-To-Disk Trigger: {}'.format(self.wricom))
        if self.wricom:
            if output_path is None:
                output_path = self.default_output_path
            #if os.path.isdir(output_path):
            #    get = input("[SOURCEPROCESS] Output Path Already Existed. Overwrite?(Y/N): ")
            #    if get in ['n','N']:
            #        print('[SOURCEPROCESS] Job Terminated.')
            #        return -1      
            #else:
            #    os.mkdir(output_path)
        audio_seg = []

        print('[SOURCEPROCESS] Begin Extraction')
        try:
            overlap = float(self.overlap)
            segt = float(self.segt)
            segnum = 0
            inp = ffmpeg.input(source)
            audi = inp['a']
            st_t = 0.0
            en_t = sp.check_output(['ffprobe','-v','error' ,'-show_entries' ,'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',source],shell=False)
            en_t = float(en_t)
            output_format = lambda output_path, segnum : output_path+'/'+'segment'+ str('%03d'%segnum)+'.'+self.encoding
            while(en_t-st_t>=self.segt):
                output = output_format(output_path, segnum)
                audi = inp['a']
                audi = audi.filter('atrim', st_t, st_t+self.segt)
                oup = ffmpeg.output(
                    audi, 'pipe:',
                    format=self.encoding, ac=self.ac, ar=self.ar)
                audio_data = ffmpeg.run(oup, capture_stdout=True)[0]
                audio_seg.append(audio_data)
                if self.wricom:
                    self.writetodisk(audio=audio_data, path=output)
                audio_data = 0
                st_t += self.segt
                st_t -= self.overlap
                segnum += 1
            output = output_format(output_path, segnum)
            audi = inp['a']
            audi = audi.filter('atrim', st_t, en_t)
            oup = ffmpeg.output(
                audi, 'pipe:',
                format=self.encoding, ac=self.ac, ar=self.ar)
            audio_data = ffmpeg.run(oup, capture_stdout=True)[0]
            audio_seg.append(audio_data)
            if self.wricom:
                self.writetodisk(audio=audio_data, path=output)

        except MemoryError:
            print('[ERROR] Extraction Unhandle Error')
        return audio_seg


if __name__ == '__main__':
    # Initial argparsing
    parser = ap.ArgumentParser()
    subpar = parser.add_subparsers(dest='command')
    cmd = subpar.add_parser('extract')
    cmd.add_argument('inputsrc',type=str,help="source of input video")
    cmd.add_argument('-f','--format',type=str,help="format of output",default='wav')
    cmd.add_argument('-ar','--audio_rate',type=str,help='sample rate',default='44100')
    cmd.add_argument('-ac','--audio_chanel',type=str,help='audio chanel',default='1')
    cmd.add_argument('-st','--segment_time',type=str,help='time(seconds) in each splited segment',default='30.0')
    cmd.add_argument('-ol','--overlap_time',type=str,help='time(seconds) of the overlap between segment',default='2.0')
    cmd.add_argument('-wd','--writeon_disk',action='store_true',help='option to write on disk')
    args = parser.parse_args()
    writing_command = False
    if args.command:
        if args.command == 'extract':
            if args.writeon_disk:
                writing_command = True
            sourceprocess().paramsparser(ac=args.audio_chanel,ar=args.audio_rate,encoding = args.format,segt=args.segment_time,overlap=args.overlap_time,writedisk=writing_command)
            sourceprocess().extract(args.inputsrc)
