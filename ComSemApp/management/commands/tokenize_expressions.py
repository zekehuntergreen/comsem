from django.core.management.base import BaseCommand, CommandError
from ComSemApp.models import Expression, SequentialWords, Word, Tag

import sys

from utils import pos_tag as comsem_pos_tag


class Command(BaseCommand):
    help = ('Drops all data from SequentialWords, Word, and Tag tables, then takes each expression, '
            'tokenizes it using nltk and the CLAW5 tagset, and inserts the relevant information into those three tables')

    def handle(self, *args, **options):
        # delete contents of SequentialWords, Word, Tag
        claws5_tagset = {
            "AJ0": "adjective (unmarked) - good, old",
            "AJC": "comparative adjective - better, older",
            "AJS": "superlative adjective - best, oldest",
            "AT0": "article - THE, A, AN",
            "AV0": "adverb (unmarked) - often, well, longer, furthest",
            "AVP": "adverb particle - up, off, out",
            "AVQ": "wh-adverb - when, how, why",
            "CJC": "coordinating conjunction - and, or",
            "CJS": "subordinating conjunction - although, when",
            "CJT": "the conjunction THAT - that",
            "CRD": "cardinal numeral - 3, fifty-five, 6609 (excl one)",
            "DPS": "possessive determiner form - your, their",
            "DT0": "general determiner - these, some",
            "DTQ": "wh-determiner - whose, which",
            "EX0": "existential THERE - there",
            "ITJ": "interjection or other isolate - oh, yes, mhm",
            "NN0": "noun (neutral for number) - aircraft, data",
            "NN1": "singular noun - pencil, goose",
            "NN2": "plural noun - pencils, geese",
            "NP0": "proper noun - London, Michael, Mars",
            "NULL": "the null tag (for items not to be tagged)",
            "ORD": "ordinal - sixth, 77th, last",
            "PNI": "indefinite pronoun - none, everything",
            "PNP": "personal pronoun - you, them, ours",
            "PNQ": "wh-pronoun - who, whoever",
            "PNX": "reflexive pronoun - itself, ourselves",
            "POS": "the possessive (or genitive morpheme) - 's or '",
            "PRF": "the preposition OF - of",
            "PRP": "preposition (except for OF) - for, above, to",
            "PUL": "punctuation - left bracket - ( or [ )",
            "PUN": "punctuation - general mark - . ! , : ; - ? ...",
            "PUQ": "punctuation - quotation mark - ` ' \"",
            "PUR": "punctuation - right bracket - ) or ]",
            "TO0": "infinitive marker TO - to",
            "UNC": "unclassified\" items which are not words of the English lexicon",
            "VBB": "the \"base forms\" of the verb \"BE\" (except the infinitive) - am, are",
            "VBD": "past form of the verb \"BE\" - was, were",
            "VBG": "-ing form of the verb \"BE\" - being",
            "VBI": "infinitive of the verb \"BE\" - be",
            "VBN": "past participle of the verb \"BE\" - been",
            "VBZ": "-s form of the verb \"BE\" - is, 's",
            "VDB": "base form of the verb \"DO\" (except the infinitive) - do",
            "VDD": "past form of the verb \"DO\" - did",
            "VDG": "-ing form of the verb \"DO\" - doing",
            "VDI": "infinitive of the verb \"DO\" - do",
            "VDN": "past participle of the verb \"DO\" - done",
            "VDZ": "-s form of the verb \"DO\" - does",
            "VHB": "base form of the verb \"HAVE\" (except the infinitive) - have",
            "VHD": "past tense form of the verb \"HAVE\" - had, 'd",
            "VHG": "-ing form of the verb \"HAVE\" - having",
            "VHI": "infinitive of the verb \"HAVE\" - have",
            "VHN": "past participle of the verb \"HAVE\" - had",
            "VHZ": "-s form of the verb \"HAVE\" - has, 's",
            "VM0": "modal auxiliary verb - can, could, will, 'll",
            "VVB": "base form of lexical verb (except the infinitive) - take, live",
            "VVD": "past tense form of lexical verb - took, lived",
            "VVG": "-ing form of lexical verb - taking, living",
            "VVI": "infinitive of lexical verb - take, live",
            "VVN": "past participle form of lex. verb - taken, lived",
            "VVZ": "-s form of lexical verb - takes, lives",
            "XX0": "the negative NOT or N'T - not",
            "ZZ0": "alphabetical symbol - A, B, c, d",
        }

        sequential_words = SequentialWords.objects.all()
        self.stdout.write(self.style.SUCCESS('Deleting %s sequential word records' % len(sequential_words)))
        sequential_words.delete()

        words = Word.objects.all()
        self.stdout.write(self.style.SUCCESS('Deleting %s word records' % len(words)))
        words.delete()

        tags = Tag.objects.all()
        self.stdout.write(self.style.SUCCESS('Deleting %s tags records' % len(tags)))
        tags.delete()


        # load the tagset
        # self.stdout.write(self.style.SUCCESS('creating %s tag records' % len(claws5_tagset)))
        # for tag in claws5_tagset:
            # Tag.objects.create(tag=tag, description=claws5_tagset[tag], frequency=0)

        # expressions
        expressions = Expression.objects.filter(worksheet__released=False) # only do this for released worksheets
        self.stdout.write(self.style.SUCCESS('processing %s expressions' % len(expressions)))

        expression_count = 1
        for expression in expressions:
            comsem_pos_tag(expression)
            expression_count += 1
            if expression_count % 100 == 0:
                print('.', end='', flush=True)
        print('')
