import sys
import io
import logging
import wave
import numpy as np
from maxfw.model import MAXModelWrapper
from deepspeech import Model
from librosa.core import resample

logger = logging.getLogger()


class ModelWrapper(MAXModelWrapper):

    MODEL_NAME = 'MAX Speech to Text Converter'
    DEFAULT_MODEL_PATH = 'assets/models/output_graph.pbmm'
    MODEL_LICENSE = "MPL-2.0"

    MODEL_META_DATA = {
        'id': '{}'.format(MODEL_NAME.lower().replace(' ', '-')),
        'name': MODEL_NAME,
        'description': 'Converts spoken words into text form.',
        'type': 'Speech-To-Text Translation',
        'license': MODEL_LICENSE,
        'source': 'https://developer.ibm.com/exchanges/models/all/max-speech-to-text-converter/'
    }

    N_FEATURES = 26  # number of MFCC features
    N_CONTEXT = 9  # Size of the context window used for producing timesteps in the input vector
    BEAM_WIDTH = 500  # Beam width used in the CTC decoder when building candidate transcriptions
    LM_ALPHA = 0.75  # The alpha hyperparameter of the CTC decoder. Language Model weight
    LM_BETA = 1.85  # The beta hyperparameter of the CTC decoder. Word insertion bonus.

    alphabet_path = 'assets/models/alphabet.txt'
    lm_path = 'assets/models/lm.binary'
    trie_path = 'assets/models/trie'

    def __init__(self, path=DEFAULT_MODEL_PATH):
        logger.info('Loading model from: {}...'.format(path))

        self.model = Model(path, self.N_FEATURES, self.N_CONTEXT, self.alphabet_path, self.BEAM_WIDTH)
        self.model.enableDecoderWithLM(self.alphabet_path, self.lm_path, self.trie_path, self.LM_ALPHA, self.LM_BETA)

        logger.info('Loaded model')

    def _convert_samplerate(self, audio_data, fs):

        resampled_audio = resample(np.frombuffer(audio_data, np.int16).astype(np.float32), fs, 16000)
        return 16000, resampled_audio.astype(np.int16)

    def _read_audio(self, audio_data):

        try:
            fin = wave.open(io.BytesIO(audio_data))
        except wave.Error:
            raise OSError("Error reading the audio file. Only WAV files are supported.")
        except EOFError:
            raise OSError("Error reading the audio file. Only WAV files are supported.")

        if fin.getnchannels() != 1:
            raise OSError("Only mono audio files are supported.")

        fin_len = fin.getnframes() / fin.getframerate()  # num frames / frame rate = length in seconds

        if fin_len > 10:
            raise OSError("This model is designed to work with short (about 5 second) audio files only.")

        return fin

    def _pre_process(self, audio_data):
        fin = self._read_audio(audio_data)
        fs = fin.getframerate()
        if fs != 16000:
            print('Warning: original sample rate ({}) is different than 16kHz. Resampling might produce erratic speech '
                  'recognition.'.format(fs), file=sys.stderr)
            fs, audio = self._convert_samplerate(audio_data, fs)
        else:
            audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)
        fin.close()
        return audio

    def _post_process(self, preds):
        return preds

    def _predict(self, x):
        preds = self.model.stt(x, 16000)
        return preds
