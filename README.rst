::

                .-'''-.
               '   _    \
       .     /   /` '.   \    _..._
     .'|    .   |     \  '  .'     '.   .--./)
   .'  |    |   '      |  '.   .-.   . /.''\\
  <    |    \    \     / / |  '   '  || |  | |
   |   | ____`.   ` ..' /  |  |   |  | \`-' /
   |   | \ .'   '-...-'`   |  |   |  | /("'`
   |   |/  .               |  |   |  | \ '---.
   |    /\  \              |  |   |  |  /'""'.\
   |   |  \  \             |  |   |  | ||     ||
   '    \  \  \            |  |   |  | \'. __//
  '------'  '---'          '--'   '--'  `'---'


kong
====

Kong is a set of tests to be run against a live cluster. Kong sees you when
you're sleeping and knows when you've been bad or good.


Quickstart
----------

You're going to want to make your own config.ini file in the /etc/ directory,
it needs to point at your running cluster.  Also you will need to provide
sample images:

    cd sample_vms
    curl -O http://images.ansolabs.com/tty.tgz
    tar -zxvf tty.tgz

After that try commands such as::

    run_tests.sh --nova
    run_tests.sh --glance
    run_tests.sh --swift


Additional Info
---------------

There are additional README files in the various subdirectories of this project.
