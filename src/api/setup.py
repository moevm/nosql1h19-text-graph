from logger import log

__all__ = ['do_setup']


def do_setup():
    log.debug(f'Starting nltk setup')
    nltk = __import__('nltk')
    nltk.download('stopwords')

    log.debug('Staring Mystem setup')
    pymystem3 = __import__('pymystem3')
    pymystem3.Mystem()

    log.debug('Setup finished')
