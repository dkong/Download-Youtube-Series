import re
import os

#title = 'Snaeha Neak Jomreang'
#title = 'Chop Jet Sneah Oun'
title = 'Snaeh oun lurs ge'

for root, dirs, files in os.walk('output'):
    for file in files:
        #match = re.match('.* (\d+)\.(\d+)', file)
        match = re.match('.* (\d+) (\d+)_', file)
        if match:
            episode = match.groups()[0]
            part = match.groups()[1]

            old_filename = os.path.join(root, file)
            new_filename = '%s %02d.%02d.mp4' % (title, int(episode), int(part))
            new_filename = os.path.join(root, new_filename)

            print 'renaming %s to %s' % (old_filename, new_filename)
            os.rename(old_filename, new_filename)
