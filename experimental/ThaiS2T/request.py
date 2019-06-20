import os
import io
import config

class SpeechAPI:
    """
    This class is for requesting of transcript of a audio file
    Attributes:
        credentials (google.credential): credential for API OAUTH2 authentication.
        client (google.cloud.client): Google cloud Speech to Text Client session.
        response (google.protobuff): Google cloud Speech to Text API response in protobuff. 
    Methods:
        Transcribe_Linear16: Transcribe audio file encoded with Linear16 (pcm_s16le) 1 of 2 lossless that Google's Speech to Text support.
    """
    def __init__(self, multi_req, **kwargs):
        """ Session Instantiator"""
        #Import GCc libs.
        #[DECLARE Global]
        global speech
        global enums
        global types
        global MessageToJson, MessageToDict

        from google.cloud import speech
        from google.cloud.speech import enums
        from google.cloud.speech import types
        from google.protobuf.json_format import MessageToJson, MessageToDict

        #Using OAUTH2 due to Credential expliciting wouldn't work (Credential Path need to be set in environment PATH instead, so using OAUTH2 seems more plausible).
        from google.oauth2 import service_account
        
        self.credentials = (
            service_account
            .Credentials.from_service_account_file(config.GOOGLE_OAUTH2_CREDS_PATH)
        )
        #[END Credential Explicition]

        #Instantiates a client.
        self.client = speech.SpeechClient(credentials=self.credentials)
        
        #Inintialize Primitive Attributes

        self.audio_list = []
        self.config = types.RecognitionConfig(
            #audio_channels = 1,
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100,
            language_code='th-TH',
            enable_word_time_offsets=True)
            #enable_word_confidence=True)
    
        if multi_req:
            self.audio = types.RecognitionAudio(content=kwargs.pop('audio'))

    def loadaudio_fromdir(self,input_path):
        """
        Load Audio Segment from specified path.
        """
        
        print('Loading from directory: {}'.format(input_path))
        file_in_dir = os.listdir(input_path)
        soundlist = [os.path.join(input_path,file_name) for file_name in file_in_dir]
        soundlist.sort()
        for sound in soundlist:
            with io.open(sound,rb) as audio_file:
                content = audio_file.read()
                self.audio_list.append(types.RecognitionAudio(content=content))

        print('{} file(s) loaded.'.format(len(file_in_dir)))
         
    def loadaudio_fromstream(self,stream_list):
        """
        Load Audio from I/O Stream directly.
        """

        print('Loading from ffmpeg IO Stream.')
        
        audio_list = []
        
        for sound in stream_list:
            audio_list.append(types.RecognitionAudio(content=sound))
        
        print('{} audio segment(s) loaded.'.format(len((stream_list))))
        
        return audio_list
        
    #Transcribe Audio file with LINEAR16 Encoding
    def Transcribe_Linear16(self, debug=False, multi_req=False, **kwargs):
        """
        Description:
        Transcribe Linear16 encoding audio.
        Parameters:
        audio: raw audio byte
        """

        print('Sending API Request')

        #Detect speech in the audio file (Sending Request)
        if not multi_req:
            self.response = self.client.recognize(self.config, kwargs.pop('audio'))
        else:
            self.response = self.client.recognize(self.config, self.audio)
        #Extract Results
        if debug:
            for result in self.response.results:
                alternative = result.alternatives[0]
                print('From file: {}'.format(file_path))
                print('Total Possible Transript: {}'.format(len(result.alternatives)))
                print('Transcript: {}'.format(alternative.transcript))
                print('Confidence: {}'.format(alternative.confidence))

                for word_info in alternative.words:
                    word = word_info.word
                    start_time = srtprocessor().timeformat(word_info.start_time.seconds, word_info.start_time.nanos*1e-3)
                    end_time = srtprocessor().timeformat(word_info.end_time.seconds, word_info.end_time.nanos*1e-9)
                    print('Word: {}, Start time: {}, End time: {}'.format(word, start_time, end_time))
        
        # <RESULT PROCESSING AND RETURN>

        # Convert Response's Protobuf to JSON format
        Metadata = MessageToJson(self.response,preserving_proto_field_name=True)
        # Convert Response's Protobuf to Dictionaries
        Results_Dict = MessageToDict(self.response,preserving_proto_field_name=True)
        # Return Raw Results, Metadata, Results_Dict
        if not multi_req:
            return self.response.results, Metadata, Results_Dict
        else:
            return Results_Dict
