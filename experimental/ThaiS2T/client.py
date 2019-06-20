import multiprocessing as mp
import simplejson as json
import os
import shutil

import config
from .preprocess import sourceprocess
from .request import SpeechAPI
from .textprocess import txtprocess, STTprocessor

# Instantiate Client
SrcProcess = sourceprocess()


# Multiprocessing Limitability bypass
def transcribe_job_multi(
        proc_num, audio, output_path, returning_dict={}, mode=2):
    if mode == 1:
        returning_dict[proc_num] = (
            SpeechAPI(multi_req=True, audio=audio)
            .Transcribe_Linear16(multi_req=True, pnum=proc_num)
        )
        filename = 'speech'+str('%03d' % proc_num)+'.json'
        print('[CLIENT] Writing {}'.format(filename))
        FileManager().json_write(
            dirpath=output_path+'/metadata/',
            path=filename, data=returning_dict[proc_num])
    elif mode == 2:
        result = (
            SpeechAPI(multi_req=True, audio=audio)
            .Transcribe_Linear16(multi_req=True, pnum=proc_num)
        )
        filename = 'speech'+str('%03d' % proc_num)+'.json'
        print('[CLIENT] Writing {}'.format(filename))
        FileManager().json_write(
            dirpath=output_path+'/metadata/',
            path=filename, data=result)
        return {proc_num: result}


class worker:

    def __init__(self, input_file,
                 audio_write=True,
                 debug=False, onload=True,
                 output_path=None,
                 multi=True, return_raw=False):
        # Display General Information
        print('[CLIENT][WORKER] Thai Automated Trannscribe (PROTOTYPE)')
        print('[CLIENT][INFO] Project: ByteArk Automated Subtitle')

        # Call DataManage
        self.manager = FileManager()
        # Check if Default Primitive Directory Existed. If not, make one.
        # primitive_dirs = ['./output', '/dump']
        # check = list(map(os.path.isdir, primitive_dirs))
        # [[os.mkdir(prm_dir) for prm_dir in primitive_dirs if boolean]
        #  for boolean in check]

        # input_path = input('[WORKER] Specified Input Path: ')
        if onload:
            # Initialize Job and Prepare Output Directory
            print('[WORKER] Streaming from source file.')
            if not os.path.isfile(input_file):
                print(input_file, os.path.isfile(input_file))
                #raise FileNotFoundError
            # if output_path is None:
            #     self.output_path = input('[WORKER] Specified Output Path: ')
            # else:
            #     self.output_path = output_path

            # os.mkdir(self.output_path)
            if output_path is None:
                self.output_path = config.STORAGE
            else:
                self.output_path = output_path

            if os.path.isdir(self.output_path):
                shutil.rmtree(self.output_path)
            os.makedirs(self.output_path+config.DEFAULT_META_DIR)
            os.makedirs(self.output_path+config.DEFAULT_TRANS_DIR)
            if audio_write:
                SrcProcess.paramsparser(writedisk=True)
            self.audio_seg = SrcProcess.extract(
                source=input_file,
                output_path=self.output_path+config.DEFAULT_META_DIR)
        if not multi:
            self.Speech = SpeechAPI(multi_req=False)
            print('[CLIENT] CLIENT INITIALIZED')
        # Debug Trigger
        print('[WORKER] DEBUGMODE Trigger: {}'.format(debug))
        self.debug = debug
        self.return_raw = return_raw
        print('[CLIENT] Ready to Work!')


    def transcribe(self,
                   from_stream=True,
                   debug=False,
                   jsonsave=False,
                   save_path=None,
                   datastore=False,
                   multi=True):

        print('[WORKER][TRANSCRIBE] Transcribe job initialized.')
        print('Current Configuration:')
        print('from_stream: {}'.format(from_stream))
        print('jsonsave: {}'.format(jsonsave))
        print('save_path: {}'.format(save_path))
        print('datastore: {}'.format(datastore))

        _, _, result_dicts_list = [], [], []
        # Full loop due to list comprehension can't create two list
        print('[WORKER][TRANSCRIBE] BEGIN TRANSCRIPTION')
        if from_stream and not multi:
            # Turn to GoogleRecognition types
            audio_list = self.Speech.loadaudio_fromstream(self.audio_seg)
        else:
            # For another method.
            pass
            # Send API Request for Transcription
        if not multi:
            for sound_index, sound in enumerate(audio_list, 0):
                _, _, result = self.Speech.Transcribe_Linear16(audio=sound)

                # results.append(result)
                # metadatas.append(metadata)
                result_dicts_list.append(result)

                # If need JSON to be written down on disk
                if jsonsave:
                    filename = 'speech'+str('%03d' % sound_index)+'.json'
                    print('[CLIENT] Writing {}'.format(filename))
                    self.manager.json_write(
                        dirpath=self.output_path+'/metadata/',
                        path=filename, data=result)
        else:
            print('[CLIENT] BEGIN MULTIPROCESSING')
            # process = []
            if config.MAX_SIMU_OUTBOUND_REQUEST != mp.cpu_count():
                print('Extend Processing to {}'.format(
                    config.MAX_SIMU_OUTBOUND_REQUEST))
                pool = mp.Pool(config.MAX_SIMU_OUTBOUND_REQUEST)
            else:
                pool = mp.Pool(mp.cpu_count())
            manager = mp.Manager()
            returning_dict = manager.dict()

            # Old mp style (no process limitation)
            # for proc_num, audio in enumerate(self.audio_seg, 0):
            #     print('[CLIENT] Processing process - {}'.format(proc_num))
            #     p = mp.Process(
            #         target=transcribe_job_multi,
            #         args=(proc_num, audio, self.output_path, returning_dict,)
            #     )
            #     process.append(p)
            #     p.start()
            # for child in process:
            #     child.join()

            result_dicts_list = [
                pool.apply_async(transcribe_job_multi,
                                 args=(
                                       proc_num,
                                       audio,
                                       self.output_path,
                                       returning_dict,))
                for proc_num, audio in enumerate(self.audio_seg, 0)]
            output = {}
            [output.update(result.get()) for result in result_dicts_list]
            result_dicts_list = []
            for pnum in range(len(output)):
                result_dicts_list.append(output[pnum])
            del output

        if debug:
            # import pprint
            # pp = pprint.PrettyPrinter()
            pass

        # Execute Job
        if self.return_raw:
            txt = txtprocess(
                result_dicts_list, debug=config.DEBUG, raw_script=True).raw_scripts
            return txt
        txt = txtprocess(
            result_dicts_list, debug=config.DEBUG).transcripts
        self.manager.json_write(
            self.output_path+config.DEFAULT_TRANS_DIR, 'sentences.json', txt)
        STTprocessor().srt_gen(
            self.output_path
            + config.DEFAULT_TRANS_DIR
            + config.DEFAULT_TRANS_NAME, txt)


class FileManager:

    def __init__(self):
        pass

    def json_write(self, dirpath, path, data):

        with open(dirpath+path, 'w') as fp:
            json.dump(data, fp, sort_keys=True, indent=4)

    def json_load(self, path):
        print('[FM] LOADS {}'.format(path))
        f = open(path)
        data = json.load(f)
        f.close()
        return data

    def json_load_dir(self, dirpath):
        print('[FM] LOAD FROM {}'.format(dirpath))
        filelist = os.listdir(dirpath)
        filelist.sort()
        contentlist = [
            self.json_load(dirpath+'/'+jsonfile) for jsonfile in filelist]

        return contentlist

    def merge_srt(self, source_vid, srt_path, output_vid):
        import ffmpeg

        source = ffmpeg.input(source_vid)
        srt = ffmpeg.input(srt_path)
        out = ffmpeg.output(
            source, srt, output_vid,
            **{'c': 'copy', 'c:s': 'mov_text'})
        out.run()
