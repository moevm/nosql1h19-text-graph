from logger import log


def do_setup():
    log.debug('Starting nltk setup')
    nltk = __import__('nltk')
    nltk.download('stopwords')

    log.debug('Staring Mystem setup')
    pymystem3 = __import__('pymystem3')
    pymystem3.Mystem()

    log.debug('Setup finished')


if __name__ == "__main__":
    do_setup()
