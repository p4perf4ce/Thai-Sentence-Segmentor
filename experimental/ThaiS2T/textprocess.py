class txtprocess:
    """
    When calling txtprocess class is called a results is required
    and automatically generate a list of sentence dict for using
    to generate srt or vtt(WIP) file.

    Args:
        results (list): A list of results(dict) obtain from
                        Google Speech to Text API which had been
                        converted to Python dict.
        alternative (int): Since single transcription can have
                           multiple alternative when on low confidence.
                           This choose which alternative we would use.
                           Default is 0.
        timeoffset (float): Time Duration per segment of segmented files.
        overlap (float): Overlap duration of segmented files.
        debug (boolean): debug trigger.

    Attributes:
        resultslist (list): Passing from results parameter.
        timefofset (float): Passing from timeoffset parameter.
        overlaptime (float): Passing from overlap parameter.
        alternative (int): Passing from alternative parameter.
        transcripts (list): A result of transcript_format method.
    """

    def __init__(self,
                 results,
                 alternative=0,
                 timeoffset=50,
                 overlap=1.25,
                 debug=False,
                 raw_script=False):

        self.resultslist = results       # Complete transcripted results list
        self.timeoffset = timeoffset     # Time durations per segment
        self.overlaptime = overlap       # Overlap time per each segment
        self.alternative = alternative   # Select alternative
        self.raw_transcript_config = {
            'results': results,
            'timeoffset': timeoffset,
            'overlap': overlap,
            'alternative': alternative
        }
        # Recursive Execution
        # Remove Overlap word from each segment (Mandatory)
        self.overlap_remove()

        if raw_script:
            self.raw_scripts = self.resultslist
        # Execute Parser
        
        self.transcripts = self.transcript_generate(debug=True)

    def tp(self, time, mode=1):
        """
        Time Processing Method.
        Parameters:
            time (str)(float): time value in seconds form.
            mode (int): Specified output format.

        Returns:
            if  mode = 1 returns time in list of [second, microsecond]
                mode = 2 returns time float in  a seconds format for
                         doing calculations.
        """

        # Just to spliting microsec from SS.mSmSs time format
        # Output format : time = [SS, mSmSmS]

        if mode == 1:
            time = str(time).replace('s', '')
            time = str('%.3f' % float(time))
            time = time.split('.')
            sectime = int(time[0])
            if len(time) == 2:
                microsec = int(time[1])
            else:
                microsec = 0
            time = [sectime, microsec]
        elif mode == 2:
            if type(time) == list and len(time) == 2:
                time = time[0] + (time[1]/(10**6))
                return time
            time = float(time.replace('s', ''))
        return time

    def overlap_remove(self):
        """
        Manipulate Raw Transcription data by directly
        remove edge case of each segment out.
        """
        print('[TXTPRO] Begin Overlap Removal')
        total_seg = len(self.resultslist)

        # Define Boundaries
        right_bound = self.timeoffset - self.overlaptime
        left_bound = self.overlaptime
        word_index = None

        # Iterate through resultslist
        for results_index in range(total_seg):

            if results_index == total_seg-1:
                break
            results_index_con = results_index+1

            # Select last result of current index and the next one
            # Find last word of left segment that's in the boundaries
            try:
                left_segment = (
                    self.resultslist[results_index]
                                    ['results'][-1]
                                    ['alternatives'][0]
                                    ['words']
                                )
            except KeyError:
                # print(self.resultslist[results_index])
                continue
            try:
                right_segment = (
                    self.resultslist[results_index_con]
                                    ['results'][0]
                                    ['alternatives'][0]
                                    ['words']
                                )
            except KeyError:
                # print(self.resultslist[results_index_con])
                continue
            # Left Segment Manipulation
            if (
                self.tp(left_segment[-1]['start_time'],
                        mode=2) > right_bound and
                    self.tp(left_segment[-1]['end_time'],
                            mode=2) == self.timeoffset):
                print(left_segment[-1]['start_time'], right_bound)
                # Delete any word that start after boundaries and end at the
                # maximum duration if not no words
                deleted_words = (
                                    self.resultslist[results_index]
                                                    ['results'][-1]
                                                    ['alternatives'][0]
                                                    ['words']
                                    .pop(word_index)
                                )
                print(deleted_words, 'left_segment')
                break  # Since it should be only one word

            # Right Segment Manipulation
            for word_index, word_info in enumerate(right_segment, 0):
                if (
                    self.tp(word_info['start_time'],
                            mode=2) < left_bound and
                        self.tp(word_info['end_time'],
                                mode=2) < left_bound):

                    deleted_words = (
                                        self.resultslist[results_index_con]
                                                        ['results'][0]
                                                        ['alternatives'][0]
                                                        ['words']
                                        .pop(word_index)
                                    )
                    print(deleted_words, 'right_segment')
                    break

        print('[TXTPRO] All Overlaps Removed.')

    def sentence_construct(self, sentence, start_time, end_time, **kwargs):
        """
        Sentence Dict Constructor.
        Parameters:
            sentence (str): Sentence string.
            start_time (list): Start time in list of [second, microsecond].
            end_time (list): end time in list of [second, microsecond].
        Returns:
            {'sentence':sentence,
             'start_time':[second, microsecond],
             'end_time':[second, microsecond]}
        """
        # transcript[0] = {'sentence':sentence,
        #                'start_time':st_t,
        #                'end_time':ed_t}
        sentence_dict = {}
        sentence_dict['sentences'] = sentence
        sentence_dict['start_time'] = start_time
        sentence_dict['end_time'] = end_time
        sentence_dict['confidence'] = kwargs.pop('confidence', None)
        sentence_dict['word_count'] = kwargs.pop('word_count', None)
        return sentence_dict

    def transcript_init(self,
                        sentence_cutoff_interval=1.500,
                        maximum_time_duration=6.200,
                        linelowerwordlim=5,
                        linewordlim=35):
        """
        Initiate Configuration for Transcript Parser
        """
        print('[TXTPRO] Initialize Transcript Configuration')

        transcript_config = {
            'sentence_cutoff_interval': sentence_cutoff_interval,
            'maximum_time_duration': maximum_time_duration,
            'linelowerwordlim': linelowerwordlim,
            'linewordlim': linewordlim
            }

        return transcript_config

    def transcript_generate(self, debug=False, nlpSegmenter=True):
        """
        Convert results list to a complete single transcription.
        Parameters:
            debug: Debug trigger.
        Returns:
            transcripts: List of Sentence dict with timestamp.
        """

        config = self.transcript_init()
        print('[TXTPRO] Begin Convert Transcripts to Sentences')

        transcript = (
            SentenceSegmentor(
                self.resultslist,
                self.raw_transcript_config,
                config)
            .transcript_worker()
        )

        print('[TXTPRO] All Transcripts have converted to Sentences')
        return transcript


class SentenceSegmentor(txtprocess):
    """
    Segment Thai String into multiple-sentence based on
    part of speech analysis and duration of speech.
    In addition, beautify the sentence to look like human-made transcript.
    """

    def __init__(self,
                 target_transcript,
                 raw_config,
                 target_config):

        # Establish Transcript Configuration.
        self.target_transcript = target_transcript
        self.raw_transcript_config = raw_config
        self.target_config = target_config

        # Get Transcript Configuration.
        self.timeoffset = self.raw_transcript_config['timeoffset']
        self.overlaptime = self.raw_transcript_config['overlap']
        self.alternative = self.raw_transcript_config['alternative']
        # Max word gap time
        self.sentence_cutoff_interval = (
            self.target_config['sentence_cutoff_interval'])
        # Maximum duration per sentence.
        self.maximum_time_duration = (
            self.target_config['maximum_time_duration'])
        # Charactor Limit per Line
        self.lower_linelimit = (
            self.target_config['linelowerwordlim']
        )
        self.linelimit = (
            self.target_config['linewordlim'])

        # Define Special Charactor
        self.numeric = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.specialchar = ['+', '-', '/', '*', '^', '.']

    def fo_word_spacing(self, word, sentence, trigger):
        import pythainlp.util as util
        # Check if Word is Thai
        numeric_trigger = False
        if sentence != '':
            numeric_trigger = (
                sentence[-1] in self.numeric and
                True in
                [True if c in self.numeric else False for c in set(word)])
        if numeric_trigger:
            word = ' ' + word
            del numeric_trigger
            return word, True
        if not util.isthai(word):
            if trigger:
                return word, True
            else:
                trigger = True
            if sentence != '':
                word = ' ' + word
        else:
            if trigger:
                word = ' ' + word
            trigger = False
        return word, trigger

    def transcript_worker(self):
        # Load NLP Libraries
        print('[SENTSEG] Loading NLP Libraries . . . ', end='')
        from pythainlp import word_tokenize, Tokenizer
        from pythainlp.tag import pos_tag
        # from pythainlp.tag.named_entity import ThaiNameTagger
        print('Done')
        # ner = ThaiNameTagger()

        # Initiate Primintive Variable
        sentence_duration = 0
        sentence_list = []
        sentence = ''
        trigger = False
        word_count = 0
        self.result_transcripts = []

        # Need to check for first occurance of speech
        first_occurrance = True

        # In each results can contain multiple results but the duration are
        # provided if it's in the same result.
        for order, results in enumerate(self.target_transcript, 1):

            result_timeoffset = (
                                    ((order-1)*self.timeoffset) -
                                    (self.overlaptime*(order-1))
                                )

            # Reset Trigger
            # Check if any transcription exist. If not skip this results.
            try:
                results['results']
            except KeyError:
                sentence_duration += self.timeoffset
                continue

            # Iterate through multiple results.
            for index, result in enumerate(results['results'], 1):

                # Define result to be more accessible.
                result = result['alternatives'][self.alternative]

                # Iterate through multiple words in alternatives list
                for word_index, word_info in enumerate(result['words'], 1):

                    word = word_info['word']
                    # print(word)
                    # Select first word only due to
                    # GoogleAPI mess first word's time offset up.

                    # word_index and index must be the 1st.
                    # Since problems happen here.

                    # Count word
                    word_count += 1

                    if word_index == 1 and index == 1:
                        # Collect start time of transcript due to
                        # google doesn't output correct start_time
                        # for the first word.
                        first_word_time = (
                                            result_timeoffset +
                                            super().tp(word_info['end_time'],
                                                       mode=2)
                                          )
                        if sentence == '':
                            time_temp = first_word_time
                        # For first occurance of word in the transcript
                        # (for a timestamp reference).
                        if first_occurrance:
                            first_occurrance = False
                            if super().tp(word_info['start_time'],
                                          mode=2) == 0:
                                sentence_time_start = super().tp(
                                    super().tp(
                                        word_info['end_time'], mode=2) - 0.75)
                                last_word_end_time = sentence_time_start
                                time_temp = super().tp(
                                    sentence_time_start, mode=2)
                            else:
                                sentence_time_start = super().tp(
                                    word_info['start_time'])
                                # Redundant Countermeasure due to GoogleS2T
                                # tends to confused music intro
                                # as an part of the speech.
                                if (
                                    super().tp(
                                        sentence_time_start,
                                        mode=2) -
                                    super().tp(
                                        word_info['end_time'],
                                        mode=2)):
                                    sentence_time_start = super().tp(
                                        super().tp(
                                            word_info['end_time'],
                                            mode=2) - 0.75)
                            sentence = word  # take first word as start word
                            last_word_end_time = super().tp(
                                word_info['end_time'],
                                mode=2)
                            continue
                        if sentence == '':
                            last_word_end_time = super().tp(
                                word_info['end_time'],
                                mode=2)

                    # Collect time info of current word
                    word_time_start = (super().tp(word_info['start_time'],
                                                  mode=2) + result_timeoffset)
                    word_time_end = (super().tp(word_info['end_time'],
                                                mode=2) + result_timeoffset)
                    word_time_delta = (word_time_end - time_temp)
                    # More Redundancies due to GoogleS2T Timestamp Unaccuracy.
                    if word_time_delta > self.sentence_cutoff_interval:
                        word_time_start = word_time_end - 0.75

                    sentence_duration += word_time_delta

                    # Sentence Cutoff Bias
                    if (
                        word_time_delta > self.sentence_cutoff_interval or
                            sentence_duration > self.maximum_time_duration):

                        if sentence_duration > self.maximum_time_duration:
                            continuity = True
                        elif sentence_duration < self.maximum_time_duration:
                            continuity = False

                        # print('Order:{}, Results_index: {},
                        #        Word: {}, Word Index:{},
                        #        Sentence_Duration: {}, Word_time_delta: {}'
                        #       .format(order, index, word,
                        #               word_index, sentence_duration,
                        #               word_time_delta))

                        # Mark Last word's end time as end time of the sentence
                        sentence_time_end = super().tp(last_word_end_time)

                        # Sentence Beautifier
                        # Conjugate Sentence with Previous one
                        # if this is too short.
                        skip = False
                        if word_count < self.lower_linelimit and continuity:
                            (
                                self.result_transcripts[-1]['sentences'][-1] +
                                sentence
                            )
                            self.result_transcripts[-1]['end_time'] = (
                                sentence_time_end)
                            skip = True
                            word_count = 0
                        if not skip:
                            new_sent = ''
                            new_word_count = 0
                            sentence_tagged = pos_tag(word_tokenize(sentence))
                            for word_tagged in sentence_tagged:
                                # word[1] is Word POS
                                # JCRG = Coordinating Conjunction
                                # JSBR = Subordinating Conjunction
                                new_word_count += 1
                                if word_tagged[1] in ['JCRG', 'JSBR']:
                                    if new_word_count > self.linelimit:
                                        # print(new_sent)
                                        sentence_list.append(new_sent)
                                        new_word_count = 0
                                        new_sent = ''
                                        new_sent += word_tagged[0]
                                    else:
                                        new_sent += ' ' + word_tagged[0]
                                    continue
                                else:
                                    new_sent += word_tagged[0]

                        if new_sent != '':
                            # print(new_sent)
                            sentence = new_sent

                        # Append Sentence to list of Sentence
                        sentence_list.append(sentence)
                        # Construct Sentence Dict.
                        sentence_dict = super().sentence_construct(
                            sentence_list,
                            sentence_time_start,
                            sentence_time_end)
                        self.result_transcripts.append(sentence_dict)
                        # print(sentence_duration)
                        # print(sentence_dict)
                        # Reset
                        new_sent = ''
                        word_count = 0
                        sentence = ''
                        sentence_list = []
                        sentence_dict = {}
                        sentence_duration = 0

                    # Add spacing for foreign words and numeric.
                    word, trigger = self.fo_word_spacing(
                        word, sentence, trigger)

                    if sentence == '':
                        sentence_time_start = super().tp(word_time_start)
                    sentence += word
                    last_word_end_time = word_time_end
                    time_temp = word_time_end

        # Append the residue
        if sentence != '':
            # print(sentence_duration)
            # print(self.tp(word_time_end))
            sentence_time_end = super().tp(
                super().tp(word_info['end_time'],
                           mode=2) + result_timeoffset)
            sentence_list.append(sentence)
            sentence_dict = super().sentence_construct(
                sentence_list,
                sentence_time_start,
                sentence_time_end)  # Construct Sentence Dict.
            # print(sentence_dict)
            self.result_transcripts.append(sentence_dict)
        return self.result_transcripts

    def sentence_parser(self):
        pass


class STTprocessor:
    """
    Description:
    a srt file managing class
    """
    def __init__(self):
        global srt
        global datetime

        import pysrt as srt
        import datetime as datetime

    # Receive seconds and convert into HH:MM:SS format
    def timeformat(self, sectime, microsec):
        import datetime
        mintime = 0
        hrtime = 0
        if sectime >= 60:
            mintime = sectime // 60
            sectime %= 60
            if mintime >= 60:
                hrtime = mintime // 60
                mintime %= 60

        # Parse time to datetime object for easily access later
        time = datetime.time(
            hrtime,
            mintime,
            int(sectime),
            int(microsec))
        return time

    # Sub-Worker for srt_gen to write in srt format
    def srt_write(self, srt_path, sequence, transcript, start_ts, end_ts):
        srt_file = open(srt_path, 'a')
        srt_file.write(
            '{}\n{:02d}:{:02d}:{:02d},{:03d} --> '
            '{:02d}:{:02d}:{:02d},{:03d}\n'
            .format(sequence,
                    start_ts.hour, start_ts.minute, start_ts.second,
                    int(start_ts.microsecond),
                    end_ts.hour, end_ts.minute, end_ts.second,
                    int(end_ts.microsecond)))
        for sentence in transcript:
            srt_file.write(
                '{}\n'.format(sentence))
        srt_file.write('\n')
        srt_file.close()

    # GENERATE SubRipFile form raw results response
    def srt_gen(self, srt_path, transcripts):

        for order, sentence_dict in enumerate(transcripts):

            start_time = self.timeformat(
                sentence_dict['start_time'][0],
                sentence_dict['start_time'][1])
            end_time = self.timeformat(
                sentence_dict['end_time'][0],
                sentence_dict['end_time'][1])
            self.srt_write(
                srt_path, order,
                sentence_dict['sentences'],
                start_time, end_time)

    def vtt_write(self, vtt_path, sequence, transcript, start_ts, end_ts):
        vtt_file = open(vtt_path, 'a')
        vtt_file.write(
            '{}\n{:02d}:{:02d}:{:02d}.{:03d} --> '
            '{:02}:{:02d}:{02d}.{:03d}\n{}\n\n'
            .format(
                sequence,
                start_ts.hour, start_ts.minute, start_ts.second,
                int(start_ts.microsecond*1e-3),
                end_ts.hour, end_ts.minute, end_ts.second,
                int(end_ts.microsecond*1e-3),
                transcript))

    def vtt_gen(self, vtt_path, transcripts, metadata=None):
        # Initialize Header and Metadata
        vtt_file = open(vtt_path, 'w')
        vtt_file.write('WEBVTT\n')
        if metadata is not None:
            vtt_file.write(metadata+'\n')
        vtt_file.close()

        for _, sentence_dict in enumerate(transcripts):
            # if not cue:
            # cue_i = ''
            start_time = self.timeformat(
                sentence_dict['start_time'][0],
                sentence_dict['start_time'][1])
            end_time = self.timeformat(
                sentence_dict['end_time'][0],
                sentence_dict['end_time'][1])
            self.vtt_write(vtt_path,
                           sentence_dict['sentence'],
                           start_time, end_time)
