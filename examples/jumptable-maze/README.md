**&lt;runtime&gt;-maze** - This example generates and solves mazes.
The maze generation steps and solution are rendered to the serial
output as ascii art.

The neat little cave-generation algorithm is taken from this
blog post, you can find more info on it here:
https://kairumagames.com/blog/cavetutorial

```
:'''':::::'''''''::::::::::::::'''':::::::::::::::::'''':::''':::::::::::::::::
: xx   '        .:::''''''''''       ''''':::::'''      ::    ::::'''''':::::::
::. xx           '     ...        .::::.   ':::                '      .::::::::
:::   xx              .:::.  .     '':::     '       ..:::..          ':'''':::
::     xx:.   ::::.    ::::::::.                    ::::::::.   ::.        .:::
::::::  x::.   ::::     ':::::::.      ..:.          ''::::::::::'          :::
:::'     x::.   :::        ''':::::.  .::::    :::..     ''':::::   .:..   .:::
:'        x:::::::: .:.    .  ::::::..:::::      ''':.      :::::    '::.   :::
:          xx::::::  '   .:::::::::::::::::         ::.    .::::::..   ':.  :::
:::   .::.   xx::::       ':''''''''''''::::::.  ::::::     :::::::::.  ::. :::
::   .::::  xx.::::.           ...       ':::::    ':::     :::::::::   :::::::
:     ::    x:::::::.      ..:::::. .:::.  ''::.   .:::      ''':::::..::::::::
::::::::.    xx''::::    .:::::::::  :::::.         ::::..      :::::::::::::::
::::::::'     xx.::::    ::::::::::    '''::::::.  ::::::::.     '''  :::::::::
::::''     x  x:::::::.    ''''':::    .   '':::  ::::::::::.          ''''::::
::       xx:xxxx '''''::::::..  ::::::::::.        ''''':::::.    ..         ':
::::::.   x:::::::.    '':::::::::::::::::::::.         ::::::.    '::..     .:
::::::'    xx::::::        ''''''''''''::::::::    ..:::''::::::..   :::.   .::
:::'       xx::::::           ..      .:::::::    ::''    ::::::::.   :::.  :::
:::  ...    xx::::::::...:.   ::::.    ''''''          ..::''':::::    '::..:::
::::::::      xx'::::::::::   :::::.   ...     ...     :::   .::::::..   ::::::
:::'''    .::.  xx ''':::::.  ::::::...::::.  ::::           ''':::::::::::::::
:::  ...  ::::.   xx   :::::.  '  ::::::::::.  ::                '''''':::  :::
:::..:::   ::::  .::xx   ':::      ''''':::::   :.          ..              :::
:::::::     ::: .:::: xx  ::::.         ::::::::::...:::.   ::::.      .    :::
:::::'    .:::  ::::    xx::::::::..     ::::::::::::::::::::::::::::::::::::::
:::'      :::   ::::.     xx:::::::'':::::::::::::::::::::::'':::::::::::::::::
::        :::   :::::      x::::''     ''''::::::::'''''''     '':::::::::  :::
::.   .:.  '    ::::        xx            .:::''''   ..     ..     '''''    :::
:::   :::        '    .:::.   xxxxxxxxxxxx '        .::     ''    .:..     .:::
:::  .::::.        ..::'''       '':::::::xxxx      ::             '''::.   :::
:::  ::::::.       ::::              '::::::::xxx        :::.     ..  :::::::::
:::    '::::.       ::::.              '''  :::::xx  xx   ::::.   ':::::'''':::
::       ::::.      ::::::::.    .::.        :::::.xx::xx  :::::.    '      :::
:       .:::::. .::::::::'':'   .::::         :::::::::: xx  '::::::..   ..::::
:  .     ':::::  :::::::       .::::: .:.      ::::::::    xx  ':::::::::::::::
::::::.   :::::   ::::::::.    :::::  :::        '::::::.  ..xx  '''::::::'':::
:::::::   ::::     '':'':::      ''   ::::::.      ::::::::::: xx    '''    :::
::::::  .::::    .      ::::..   ..:::::::::::..    :::::::::    xxxxxxxxxxx:::
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
```

Also, the maze generation/solver are written in Rust, and the kernel in C.

Also also, the maze generation and maze solver are separate boxes that
share RAM, with the maze generation getting clobbered when the system brings
up the maze solving box.

This example is a good showcase of several RAM-based data structures and
very unpredictable branching patterns. It's literally solving a maze.

The largest input is a 160x160 byte maze.

More info in the [README.md](/README.md).
