# -*- coding: utf-8 -*-

import os, datetime
import tempfile
from mutagen import File
from PIL import Image
from PyQt4 import QtCore, QtGui
import subprocess, win32api
ROOT_PATH = os.getcwd()

cover_size = 140

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

def get_taskbar():
    import platform
    if platform.version()[:3] == '6.1': # Check for win7
        import ctypes
        myappid = 'fabiodiniz.gokya.supergokya' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        import comtypes.client as cc
        cc.GetModule("TaskbarLib.tlb")
        import comtypes.gen.TaskbarLib as tbl
        taskbar = cc.CreateObject(
        "{56FDF344-FD6D-11d0-958A-006097C9A090}",
        interface=tbl.ITaskbarList3)
        taskbar.HrInit()
    else:
        taskbar = None
    return taskbar

def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func
    return decorate

def getPrettyName(song_file):
    return _fromUtf8(str(song_file.tags.get('TPE1','')) + ' - ' + str(song_file.tags.get('TALB','')) + ' - ' + str(song_file.tags.get('TIT2','')))

def getSongName(url):
    return get_song_info(url)[0]

def getCoverArtPixmap(url):
    return getCoverArt(url)[1]

def clean_path(path):
    path = os.path.abspath(path)
    path = os.path.normpath(path)
    return os.path.normcase(path)

def get_song_info(name, song_file=None):
    if song_file is None:
        song_file = File(name)
    if song_file.tags:
        return [unicode(song_file.tags.get('TIT2',os.path.basename(name))),
                unicode(song_file.tags.get('TALB','')),
                unicode(song_file.tags.get('TPE1',''))]
    return [os.path.basename(name),'','']

def getCoverArt(url, song_file=None):
    global cover_size
    url = url.replace('/', '\\')
    if song_file is None:
        song_file = File(url)
    folder = os.path.join(url[:url.rfind('\\')], 'folder.jpg')
    album_name = get_cover_hash(song_file)
    iconpath = u":/png/media/nocover.png" #pessimist
    try:
        if song_file.tags and (song_file.tags.get('APIC:','') or song_file.tags.get('APIC:cover','')) and album_name:
            artwork = get_cover_ultimate(song_file)
            iconpath = os.path.join(ROOT_PATH,'cover_cache',album_name+'.png')
            iconpath_jpg = os.path.join(ROOT_PATH,'cover_cache',album_name+'.jpg')
            if not os.path.exists(iconpath):
                with open(iconpath_jpg, 'wb') as img:
                    img.write(artwork.data)
                print iconpath_jpg
                im = Image.open(iconpath_jpg)
                #im = im.resize((cover_size, cover_size), Image.ANTIALIAS)
                im.thumbnail((cover_size,cover_size), Image.ANTIALIAS)
                im.save(iconpath)
                try:
                    os.remove(iconpath_jpg)
                except:
                    pass
                #pygame.image.save(pygame.image.load(iconpath_jpg),iconpath)

            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(artwork.data)
            return [iconpath, pixmap]
        elif os.path.exists(folder) and album_name:
            iconpath = os.path.join(ROOT_PATH,'cover_cache',album_name+'.png')
            im = Image.open(folder)
            #im = im.resize((cover_size, cover_size), Image.ANTIALIAS)
            im.thumbnail((cover_size,cover_size), Image.ANTIALIAS)
            im.save(iconpath)
            #pygame.image.save(pygame.image.load(folder),iconpath)
    except Exception as e:
        open('bandicoot','a').write(str(datetime.datetime.now()) + '\t ' + str(e) + ' - ' + iconpath + '\n')
        iconpath = u":/png/media/nocover.png" #pessimist
    icon = QtGui.QIcon(iconpath)
    pixmap = icon.pixmap(cover_size, cover_size)
    return [iconpath, pixmap]

def dirEntries(dir_name, subdir, *args):
    '''Return a list of file names found in directory 'dir_name'
    If 'subdir' is True, recursively access subdirectories under 'dir_name'.
    Additional arguments, if any, are file extensions to match filenames. Matched
        file names are added to the list.
    If there are no additional arguments, all files found in the directory are
        added to the list.
    Example usage: fileList = dir_list(r'H:\TEMP', False, 'txt', 'py')
        Only files with 'txt' and 'py' extensions will be added to the list.
    Example usage: fileList = dir_list(r'H:\TEMP', True)
        All files and all the files in subdirectories under H:\TEMP will be added
        to the list.
    '''
    fileList = []
    for file_ in os.listdir(dir_name):
        dirfile = os.path.join(dir_name, file_)
        if os.path.isfile(dirfile):
            if len(args) == 0:
                fileList.append(dirfile)
            else:
                if os.path.splitext(dirfile)[1][1:] in args:
                    fileList.append(dirfile)
        # recursively access file names in subdirectories
        elif os.path.isdir(dirfile) and subdir:
            fileList += dirEntries(dirfile, subdir, *args)
    return fileList

def gen_file_name(s):
    return "".join([x for x in s if x.isalpha() or x.isdigit()])

def get_cover_hash(song_file):
    if not song_file:
        return ''
    name = str(song_file.tags.get('TPE1',''))+'_'+str(song_file.tags.get('TALB',''))
    return gen_file_name(name.decode('ascii', 'ignore'))

def get_cover_ultimate(song_file):
    if 'APIC:' in song_file.tags:
        return song_file.tags['APIC:']
    elif 'APIC:cover' in song_file.tags:
        return song_file.tags['APIC:cover']
    else:
        return type('',(object,),{'data':''})()


def get_full_song_info(name):
    """ Supposed to return REAL song data. Track, name, artist, album and cover """
    song_file = File(name)
    if song_file.tags:
        return [unicode(song_file.tags.get('TRCK','')),
                unicode(song_file.tags.get('TIT2','')),
                unicode(song_file.tags.get('TPE1','')),
                unicode(song_file.tags.get('TALB','')),
                get_cover_ultimate(song_file).data]
    return ['','','','','']


pokemons = ['Bulbasaur',
'Ivysaur',
'Venusaur',
'Charmander',
'Charmeleon',
'Charizard',
'Squirtle',
'Wartortle',
'Blastoise',
'Caterpie',
'Metapod',
'Butterfree',
'Weedle',
'Kakuna',
'Beedrill',
'Pidgey',
'Pidgeotto',
'Pidgeot',
'Rattata',
'Raticate',
'Spearow',
'Fearow',
'Ekans',
'Arbok',
'Pikachu',
'Raichu',
'Sandshrew',
'Sandslash',
'Nidoran♀',
'Nidorina',
'Nidoqueen',
'Nidoran♂',
'Nidorino',
'Nidoking',
'Clefairy',
'Clefable',
'Vulpix',
'Ninetales',
'Jigglypuff',
'Wigglytuff',
'Zubat',
'Golbat',
'Oddish',
'Gloom',
'Vileplume',
'Paras',
'Parasect',
'Venonat',
'Venomoth',
'Diglett',
'Dugtrio',
'Meowth',
'Persian',
'Psyduck',
'Golduck',
'Mankey',
'Primeape',
'Growlithe',
'Arcanine',
'Poliwag',
'Poliwhirl',
'Poliwrath',
'Abra',
'Kadabra',
'Alakazam',
'Machop',
'Machoke',
'Machamp',
'Bellsprout',
'Weepinbell',
'Victreebel',
'Tentacool',
'Tentacruel',
'Geodude',
'Graveler',
'Golem',
'Ponyta',
'Rapidash',
'Slowpoke',
'Slowbro',
'Magnemite',
'Magneton',
'Farfetch',
'Doduo',
'Dodrio',
'Seel',
'Dewgong',
'Grimer',
'Muk',
'Shellder',
'Cloyster',
'Gastly',
'Haunter',
'Gengar',
'Onix',
'Drowzee',
'Hypno',
'Krabby',
'Kingler',
'Voltorb',
'Electrode',
'Exeggcute',
'Exeggutor',
'Cubone',
'Marowak',
'Hitmonlee',
'Hitmonchan',
'Lickitung',
'Koffing',
'Weezing',
'Rhyhorn',
'Rhydon',
'Chansey',
'Tangela',
'Kangaskhan',
'Horsea',
'Seadra',
'Goldeen',
'Seaking',
'Staryu',
'Starmie',
'Mr',
'Scyther',
'Jynx',
'Electabuzz',
'Magmar',
'Pinsir',
'Tauros',
'Magikarp',
'Gyarados',
'Lapras',
'Ditto',
'Eevee',
'Vaporeon',
'Jolteon',
'Flareon',
'Porygon',
'Omanyte',
'Omastar',
'Kabuto',
'Kabutops',
'Aerodactyl',
'Snorlax',
'Articuno',
'Zapdos',
'Moltres',
'Dratini',
'Dragonair',
'Dragonite',
'Mewtwo',
'Mew',
'Chikorita',
'Bayleef',
'Meganium',
'Cyndaquil',
'Quilava',
'Typhlosion',
'Totodile',
'Croconaw',
'Feraligatr',
'Sentret',
'Furret',
'Hoothoot',
'Noctowl',
'Ledyba',
'Ledian',
'Spinarak',
'Ariados',
'Crobat',
'Chinchou',
'Lanturn',
'Pichu',
'Cleffa',
'Igglybuff',
'Togepi',
'Togetic',
'Natu',
'Xatu',
'Mareep',
'Flaaffy',
'Ampharos',
'Bellossom',
'Marill',
'Azumarill',
'Sudowoodo',
'Politoed',
'Hoppip',
'Skiploom',
'Jumpluff',
'Aipom',
'Sunkern',
'Sunflora',
'Yanma',
'Wooper',
'Quagsire',
'Espeon',
'Umbreon',
'Murkrow',
'Slowking',
'Misdreavus',
'Unown',
'Wobbuffet',
'Girafarig',
'Pineco',
'Forretress',
'Dunsparce',
'Gligar',
'Steelix',
'Snubbull',
'Granbull',
'Qwilfish',
'Scizor',
'Shuckle',
'Heracross',
'Sneasel',
'Teddiursa',
'Ursaring',
'Slugma',
'Magcargo',
'Swinub',
'Piloswine',
'Corsola',
'Remoraid',
'Octillery',
'Delibird',
'Mantine',
'Skarmory',
'Houndour',
'Houndoom',
'Kingdra',
'Phanpy',
'Donphan',
'Porygon2',
'Stantler',
'Smeargle',
'Tyrogue',
'Hitmontop',
'Smoochum',
'Elekid',
'Magby',
'Miltank',
'Blissey',
'Raikou',
'Entei',
'Suicune',
'Larvitar',
'Pupitar',
'Tyranitar',
'Lugia',
'Ho',
'Celebi']

adjectives = ['aback',
'abaft',
'abandoned',
'abashed',
'aberrant',
'abhorrent',
'abiding',
'abject',
'ablaze',
'able',
'abnormal',
'aboard',
'aboriginal',
'abortive',
'abounding',
'abrasive',
'abrupt',
'absent',
'absorbed',
'absorbing',
'abstracted',
'absurd',
'abundant',
'abusive',
'acceptable',
'accessible',
'accidental',
'accurate',
'acid',
'acidic',
'acoustic',
'acrid',
'actually',
'ad hoc',
'adamant',
'adaptable',
'addicted',
'adhesive',
'adjoining',
'adorable',
'adventurous',
'afraid',
'aggressive',
'agonizing',
'agreeable',
'ahead',
'ajar',
'alcoholic',
'alert',
'alike',
'alive',
'alleged',
'alluring',
'aloof',
'amazing',
'ambiguous',
'ambitious',
'amuck',
'amused',
'amusing',
'ancient',
'angry',
'animated',
'annoyed',
'annoying',
'anxious',
'apathetic',
'aquatic',
'aromatic',
'arrogant',
'ashamed',
'aspiring',
'assorted',
'astonishing',
'attractive',
'auspicious',
'automatic',
'available',
'average',
'awake',
'aware',
'awesome',
'awful',
'axiomatic',
'bad',
'barbarous',
'bashful',
'bawdy',
'beautiful',
'befitting',
'belligerent',
'beneficial',
'bent',
'berserk',
'best',
'better',
'bewildered',
'big',
'billowy',
'bite-sized',
'bitter',
'bizarre',
'black',
'black-and-white',
'bloody',
'blue',
'blue-eyed',
'blushing',
'boiling',
'boorish',
'bored',
'boring',
'bouncy',
'boundless',
'brainy',
'brash',
'brave',
'brawny',
'breakable',
'breezy',
'brief',
'bright',
'bright',
'broad',
'broken',
'brown',
'bumpy',
'burly',
'bustling',
'busy',
'cagey',
'calculating',
'callous',
'calm',
'capable',
'capricious',
'careful',
'careless',
'caring',
'cautious',
'ceaseless',
'certain',
'changeable',
'charming',
'cheap',
'cheerful',
'chemical',
'chief',
'childlike',
'chilly',
'chivalrous',
'chubby',
'chunky',
'clammy',
'classy',
'clean',
'clear',
'clever',
'cloistered',
'cloudy',
'closed',
'clumsy',
'cluttered',
'coherent',
'cold',
'colorful',
'colossal',
'combative',
'comfortable',
'common',
'complete',
'complex',
'concerned',
'condemned',
'confused',
'conscious',
'cooing',
'cool',
'cooperative',
'coordinated',
'courageous',
'cowardly',
'crabby',
'craven',
'crazy',
'creepy',
'crooked',
'crowded',
'cruel',
'cuddly',
'cultured',
'cumbersome',
'curious',
'curly',
'curved',
'curvy',
'cut',
'cute',
'cute',
'cynical',
'daffy',
'daily',
'damaged',
'damaging',
'damp',
'dangerous',
'dapper',
'dark',
'dashing',
'dazzling',
'dead',
'deadpan',
'deafening',
'dear',
'debonair',
'decisive',
'decorous',
'deep',
'deeply',
'defeated',
'defective',
'defiant',
'delicate',
'delicious',
'delightful',
'demonic',
'delirious',
'dependent',
'depressed',
'deranged',
'descriptive',
'deserted',
'detailed',
'determined',
'devilish',
'didactic',
'different',
'difficult',
'diligent',
'direful',
'dirty',
'disagreeable',
'disastrous',
'discreet',
'disgusted',
'disgusting',
'disillusioned',
'dispensable',
'distinct',
'disturbed',
'divergent',
'dizzy',
'domineering',
'doubtful',
'drab',
'draconian',
'dramatic',
'dreary',
'drunk',
'dry',
'dull',
'dusty',
'dusty',
'dynamic',
'dysfunctional',
'eager',
'early',
'earsplitting',
'earthy',
'easy',
'eatable',
'economic',
'educated',
'efficacious',
'efficient',
'eight',
'elastic',
'elated',
'elderly',
'electric',
'elegant',
'elfin',
'elite',
'embarrassed',
'eminent',
'empty',
'enchanted',
'enchanting',
'encouraging',
'endurable',
'energetic',
'enormous',
'entertaining',
'enthusiastic',
'envious',
'equable',
'equal',
'erect',
'erratic',
'ethereal',
'evanescent',
'evasive',
'even',
'excellent',
'excited',
'exciting',
'exclusive',
'exotic',
'expensive',
'extra-large',
'extra-small',
'exuberant',
'exultant',
'fabulous',
'faded',
'faint',
'fair',
'faithful',
'fallacious',
'false',
'familiar',
'famous',
'fanatical',
'fancy',
'fantastic',
'far',
'far-flung',
'fascinated',
'fast',
'fat',
'faulty',
'fearful',
'fearless',
'feeble',
'feigned',
'female',
'fertile',
'festive',
'few',
'fierce',
'filthy',
'fine',
'finicky',
'first',
'five',
'fixed',
'flagrant',
'flaky',
'flashy',
'flat',
'flawless',
'flimsy',
'flippant',
'flowery',
'fluffy',
'fluttering',
'foamy',
'foolish',
'foregoing',
'forgetful',
'fortunate',
'four',
'frail',
'fragile',
'frantic',
'free',
'freezing',
'frequent',
'fresh',
'fretful',
'friendly',
'frightened',
'frightening',
'full',
'fumbling',
'functional',
'funny',
'furry',
'furtive',
'future',
'futuristic',
'fuzzy',
 '',
'gabby',
'gainful',
'gamy',
'gaping',
'garrulous',
'gaudy',
'general',
'gentle',
'giant',
'giddy',
'gifted',
'gigantic',
'glamorous',
'gleaming',
'glib',
'glistening',
'glorious',
'glossy',
'godly',
'good',
'goofy',
'gorgeous',
'graceful',
'grandiose',
'grateful',
'gratis',
'gray',
'greasy',
'great',
'greedy',
'green',
'grey',
'grieving',
'groovy',
'grotesque',
'grouchy',
'grubby',
'gruesome',
'grumpy',
'guarded',
'guiltless',
'gullible',
'gusty',
'guttural',
'habitual',
'half',
'hallowed',
'halting',
'handsome',
'handsomely',
'handy',
'hanging',
'hapless',
'happy',
'hard',
'hard-to-find',
'harmonious',
'harsh',
'hateful',
'heady',
'healthy',
'heartbreaking',
'heavenly',
'heavy',
'hellish',
'helpful',
'helpless',
'hesitant',
'hideous',
'high',
'highfalutin',
'high-pitched',
'hilarious',
'hissing',
'historical',
'holistic',
'hollow',
'homeless',
'homely',
'honorable',
'horrible',
'hospitable',
'hot',
'huge',
'hulking',
'humdrum',
'humorous',
'hungry',
'hurried',
'hurt',
'hushed',
'husky',
'hypnotic',
'hysterical',
'icky',
'icy',
'idiotic',
'ignorant',
'ill',
'illegal',
'ill-fated',
'ill-informed',
'illustrious',
'imaginary',
'immense',
'imminent',
'impartial',
'imperfect',
'impolite',
'important',
'imported',
'impossible',
'incandescent',
'incompetent',
'inconclusive',
'industrious',
'incredible',
'inexpensive',
'infamous',
'innate',
'innocent',
'inquisitive',
'insidious',
'instinctive',
'intelligent',
'interesting',
'internal',
'invincible',
'irate',
'irritating',
'itchy',
'jaded',
'jagged',
'jazzy',
'jealous',
'jittery',
'jobless',
'jolly',
'joyous',
'judicious',
'juicy',
'jumbled',
'jumpy',
'juvenile',
'kaput',
'keen',
'kind',
'kindhearted',
'kindly',
'knotty',
'knowing',
'knowledgeable',
'known',
'labored',
'lackadaisical',
'lacking',
'lame',
'lamentable',
'languid',
'large',
'last',
'late',
'laughable',
'lavish',
'lazy',
'lean',
'learned',
'left',
'legal',
'lethal',
'level',
'lewd',
'light',
'like',
'likeable',
'limping',
'literate',
'little',
'lively',
'lively',
'living',
'lonely',
'long',
'longing',
'long-term',
'loose',
'lopsided',
'loud',
'loutish',
'lovely',
'loving',
'low',
'lowly',
'lucky',
'ludicrous',
'lumpy',
'lush',
'luxuriant',
'lying',
'lyrical',
'macabre',
'macho',
'maddening',
'madly',
'magenta',
'magical',
'magnificent',
'majestic',
'makeshift',
'male',
'malicious',
'mammoth',
'maniacal',
'many',
'marked',
'massive',
'married',
'marvelous',
'material',
'materialistic',
'mature',
'mean',
'measly',
'meaty',
'medical',
'meek',
'mellow',
'melodic',
'melted',
'merciful',
'mere',
'messy',
'mighty',
'military',
'milky',
'mindless',
'miniature',
'minor',
'miscreant',
'misty',
'mixed',
'moaning',
'modern',
'moldy',
'momentous',
'motionless',
'mountainous',
'muddled',
'mundane',
'murky',
'mushy',
'mute',
'mysterious',
'naive',
'nappy',
'narrow',
'nasty',
'natural',
'naughty',
'nauseating',
'near',
'neat',
'nebulous',
'necessary',
'needless',
'needy',
'neighborly',
'nervous',
'new',
'next',
'nice',
'nifty',
'nimble',
'nine',
'nippy',
'noiseless',
'noisy',
'nonchalant',
'nondescript',
'nonstop',
'normal',
'nostalgic',
'nosy',
'noxious',
'null',
'numberless',
'numerous',
'nutritious',
'nutty',
'oafish',
'obedient',
'obeisant',
'obese',
'obnoxious',
'obscene',
'obsequious',
'observant',
'obsolete',
'obtainable',
'oceanic',
'odd',
'offbeat',
'old',
'old-fashioned',
'omniscient',
'one',
'onerous',
'open',
'opposite',
'optimal',
'orange',
'ordinary',
'organic',
'ossified',
'outgoing',
'outrageous',
'outstanding',
'oval',
'overconfident',
'overjoyed',
'overrated',
'overt',
'overwrought',
'painful',
'painstaking',
'pale',
'paltry',
'panicky',
'panoramic',
'parallel',
'parched',
'parsimonious',
'past',
'pastoral',
'pathetic',
'peaceful',
'penitent',
'perfect',
'periodic',
'permissible',
'perpetual',
'petite',
'petite',
'phobic',
'physical',
'picayune',
'pink',
'piquant',
'placid',
'plain',
'plant',
'plastic',
'plausible',
'pleasant',
'plucky',
'pointless',
'poised',
'polite',
'political',
'poor',
'possessive',
'possible',
'powerful',
'precious',
'premium',
'present',
'pretty',
'previous',
'pricey',
'prickly',
'private',
'probable',
'productive',
'profuse',
'protective',
'proud',
'psychedelic',
'psychotic',
'public',
'puffy',
'pumped',
'puny',
'purple',
'purring',
'pushy',
'puzzled',
'puzzling',
'quack',
'quaint',
'quarrelsome',
'questionable',
'quick',
'quickest',
'quiet',
'quirky',
'quixotic',
'quizzical',
'rabid',
'racial',
'ragged',
'rainy',
'rambunctious',
'rampant',
'rapid',
'rare',
'raspy',
'ratty',
'ready',
'real',
'rebel',
'receptive',
'recondite',
'red',
'redundant',
'reflective',
'regular',
'relieved',
'remarkable',
'reminiscent',
'repulsive',
'resolute',
'resonant',
'responsible',
'rhetorical',
'rich',
'right',
'righteous',
'rightful',
'rigid',
'ripe',
'ritzy',
'roasted',
'robust',
'romantic',
'roomy',
'rotten',
'rough',
'round',
'royal',
'ruddy',
'rude',
'rural',
'rustic',
'ruthless',
'sable',
'sad',
'safe',
'salty',
'same',
'sassy',
'satisfying',
'savory',
'scandalous',
'scarce',
'scared',
'scary',
'scattered',
'scientific',
'scintillating',
'scrawny',
'screeching',
'second',
'second-hand',
'secret',
'secretive',
'sedate',
'seemly',
'selective',
'selfish',
'separate',
'serious',
'shaggy',
'shaky',
'shallow',
'sharp',
'shiny',
'shivering',
'shocking',
'short',
'shrill',
'shut',
'shy',
'sick',
'silent',
'silent',
'silky',
'silly',
'simple',
'simplistic',
'sincere',
'six',
'skillful',
'skinny',
'sleepy',
'slim',
'slimy',
'slippery',
'sloppy',
'slow',
'small',
'smart',
'smelly',
'smiling',
'smoggy',
'smooth',
'sneaky',
'snobbish',
'snotty',
'soft',
'soggy',
'solid',
'somber',
'sophisticated',
'sordid',
'sore',
'sore',
'sour',
'sparkling',
'special',
'spectacular',
'spicy',
'spiffy',
'spiky',
'spiritual',
'spiteful',
'splendid',
'spooky',
'spotless',
'spotted',
'spotty',
'spurious',
'squalid',
'square',
'squealing',
'squeamish',
'staking',
'stale',
'standing',
'statuesque',
'steadfast',
'steady',
'steep',
'stereotyped',
'sticky',
'stiff',
'stimulating',
'stingy',
'stormy',
'straight',
'strange',
'striped',
'strong',
'stupendous',
'stupid',
'sturdy',
'subdued',
'subsequent',
'substantial',
'successful',
'succinct',
'sudden',
'sulky',
'super',
'superb',
'superficial',
'supreme',
'swanky',
'sweet',
'sweltering',
'swift',
'symptomatic',
'synonymous',
'taboo',
'tacit',
'tacky',
'talented',
'tall',
'tame',
'tan',
'tangible',
'tangy',
'tart',
'tasteful',
'tasteless',
'tasty',
'tawdry',
'tearful',
'tedious',
'teeny',
'teeny-tiny',
'telling',
'temporary',
'ten',
'tender',
'tense',
'tense',
'tenuous',
'terrible',
'terrific',
'tested',
'testy',
'thankful',
'therapeutic',
'thick',
'thin',
'thinkable',
'third',
'thirsty',
'thirsty',
'thoughtful',
'thoughtless',
'threatening',
'three',
'thundering',
'tidy',
'tight',
'tightfisted',
'tiny',
'tired',
'tiresome',
'toothsome',
'torpid',
'tough',
'towering',
'tranquil',
'trashy',
'tremendous',
'tricky',
'trite',
'troubled',
'truculent',
'true',
'truthful',
'two',
'typical',
'ubiquitous',
'ugliest',
'ugly',
'ultra',
'unable',
'unaccountable',
'unadvised',
'unarmed',
'unbecoming',
'unbiased',
'uncovered',
'understood',
'undesirable',
'unequal',
'unequaled',
'uneven',
'unhealthy',
'uninterested',
'unique',
'unkempt',
'unknown',
'unnatural',
'unruly',
'unsightly',
'unsuitable',
'untidy',
'unused',
'unusual',
'unwieldy',
'unwritten',
'upbeat',
'uppity',
'upset',
'uptight',
'used',
'useful',
'useless',
'utopian',
'utter',
'uttermost',
'vacuous',
'vagabond',
'vague',
'valuable',
'various',
'vast',
'vengeful',
'venomous',
'verdant',
'versed',
'victorious',
'vigorous',
'violent',
'violet',
'vivacious',
'voiceless',
'volatile',
'voracious',
'vulgar',
'wacky',
'waggish',
'waiting',
'wakeful',
'wandering',
'wanting',
'warlike',
'warm',
'wary',
'wasteful',
'watery',
'weak',
'wealthy',
'weary',
'well-groomed',
'well-made',
'well-off',
'well-to-do',
'wet',
'whimsical',
'whispering',
'white',
'whole',
'wholesale',
'wicked',
'wide',
'wide-eyed',
'wiggly',
'wild',
'willing',
'windy',
'wiry',
'wise',
'wistful',
'witty',
'woebegone',
'womanly',
'wonderful',
'wooden',
'woozy',
'workable',
'worried',
'worthless',
'wrathful',
'wretched',
'wrong',
'wry',
'yellow',
'yielding',
'young',
'youthful',
'yummy',
'zany',
'zealous',
'zesty',
'zippy',
'zonked']

import random

def get_random_name():
    return random.choice(adjectives).capitalize() + ' ' + random.choice(pokemons).capitalize()