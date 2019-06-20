# Thai Automated Transcriber

# Documentation

- Preprocessing
- Transcribing
- Post-Processing

## Preprocessing
Preprocessing jobs are located in preprocess.py in root directory of this project. Thus this documentation tells whats going on in the workflow
- ### mpworker
  This is a single class in preprocess.py contain method of following:
  - **init** parameter:(outputdir='PATH')

    ATTRIBUTE
      - **outputdir**
      
        Define output directory path. If such a path does not exist. mpworker will create the directory by in path user input.
      - **ffmpeg**
      
        Define ffmpeg executable path
      
      - **platform**
        
        Contains value of the platform of this instance are running on.
  
  - **extract** parameter:(outputpath='OUTPUTPATH',encoding='ENCODING',is_segment='BOOLEAN',seg_time='TIME_VALUE',DEBUG='BOOLEAN')
    This method extract audio file from video file and re-encode into various format.
    Currently support following audio format:
      - mp3
      - Linear16 (pcm_s16le) in .wav
      - FLAC (Currently unable to do segmentation with this format)
  - **play** parameter:(path='FILEPATH', encoding='ENCODING', ac='AUDIOCHANNEL', ar='AUDIOSAMPLERATE')
    
    Play an audio file with ffplay by specific parameters.

### Transcribing
We currently use Google Cloud Speech to Text API to transcribe sentence from our preprocessed audio file. The API caller and other related jobs are located in request.py in root directory of this project.
- #### SpeechAPI
  This is API caller class. When Called, API Client is instantiated with class. 
  In this class contain many attributes and methods in following:
  
  ATTRIBUTE

    - **credentials** 
      
      Contain credential file path (JSON).
    - **client**

      SpeechAPIClient object.