import os
import torch
from torch.autograd import Variable
import pickle

"""
Note: The meaning of batch_size in PTB is different from that in MNIST example. In MNIST, 
batch_size is the # of sample data that is considered in each iteration; in PTB, however,
it is the number of segments to speed up computation. 

The goal of PTB is to train a language model to predict the next word.
"""
cwd = os.getcwd()
print('current dir, ',cwd)

def data_generator(args):
    cwd = os.getcwd()
    #print('current dir, ',cwd)
    if os.path.exists(r'"/home/hamdi/TCN/word_cnn/data/penn/penncorpus"') and not args.corpus:
        corpus = pickle.load(open(r'/home/hamdi/TCN/word_cnn/data/penn/corpus', 'rb'))
    else:
        corpus = Corpus(args.data)
        pickle.dump(corpus, open(r"/home/hamdi/TCN/word_cnn/data/penn/corpus", 'wb'))
    return corpus


class Dictionary(object):
    def __init__(self):
        self.word2idx = {}
        self.idx2word = []

    def add_word(self, word):
        if word not in self.word2idx:
            self.idx2word.append(word)
            self.word2idx[word] = len(self.idx2word) - 1
        return self.word2idx[word]

    def __len__(self):
        return len(self.idx2word)


class Corpus(object):
    def __init__(self, path):
        cwd = os.getcwd()
        self.dictionary = Dictionary()
        train_path = os.path.join(cwd, r"/data/penn/train.txt")
        print(train_path)
        valid_path = os.path.join(cwd, r"/data/penn/valid.txt")
        test_path = os.path.join(cwd, r"/data/penn/test.txt")
        self.train = self.tokenize(r"/home/hamdi/TCN/word_cnn/data/penn/train.txt")
        self.valid = self.tokenize(r"/home/hamdi/TCN/word_cnn/data/penn/valid.txt")
        self.test  = self.tokenize(r"/home/hamdi/TCN/word_cnn/data/penn/test.txt")

    def tokenize(self, path):
        """Tokenizes a text file."""
        #assert os.path.exists(path)
        # Add words to the dictionary
        with open(path, 'r', encoding = 'utf8') as f:
            tokens = 0
            for line in f:
                words = line.split() + ['<eos>']
                tokens += len(words)
                for word in words:
                    self.dictionary.add_word(word)

        # Tokenize file content
        with open(path, 'r', encoding = 'utf8') as f:
            ids = torch.LongTensor(tokens)
            token = 0
            for line in f:
                words = line.split() + ['<eos>']
                for word in words:
                    ids[token] = self.dictionary.word2idx[word]
                    token += 1

        return ids


def batchify(data, batch_size, args):
    """The output should have size [L x batch_size], where L could be a long sequence length"""
    # Work out how cleanly we can divide the dataset into batch_size parts (i.e. continuous seqs).
    nbatch = data.size(0) // batch_size
    # Trim off any extra elements that wouldn't cleanly fit (remainders).
    data = data.narrow(0, 0, nbatch * batch_size)
    # Evenly divide the data across the batch_size batches.
    data = data.view(batch_size, -1)
    if args.cuda:
        data = data.cuda(1)
    return data


def get_batch(source, i, args, seq_len=None, evaluation=False):
    seq_len = min(seq_len if seq_len else args.seq_len, source.size(1) - 1 - i)
    data = Variable(source[:, i:i+seq_len], volatile=evaluation)
    target = Variable(source[:, i+1:i+1+seq_len])     # CAUTION: This is un-flattened!
    return data, target
