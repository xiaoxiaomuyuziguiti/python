import re
str1 = 'PT3H58M'
str2 = 'PT45M'

matches = re.match(r'\w\w(\d*)H?(\d*)M?', str2)
if matches.group(1) != '' and matches.group(2) != '':
    print(int(matches.group(1)) * 60 + int(matches.group(2)))
elif matches.group(1) != '' and matches.group(2) == '':
    print(int(matches.group(1)) * 60)
elif matches.group(1) == '' and matches.group(2) != '':
    print(int(matches.group(2)))
else:
    print(0)