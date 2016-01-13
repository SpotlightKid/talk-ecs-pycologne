Einführung in Entity Component Systems
======================================

Dieses Repository enthält die Slides und Beispielskripte für meinen Kurzvotrag
über *Entity Component Systems* beim Treffen der PyCologne_, der *Python User
Group Köln* am 13. Januar 2016.

Um die Beispiele auszuführen, müssen folgende Abhängigkeiten installiert
werden:

* esper_
* pyglet_

Installation:

::

    virtualenv venv
    source venv/bin/activate
    (venv)$ pip install pyglet
    (venv)$ git clone https://github.com/benmoran56/esper.git
    (venv)$ cd esper
    (venv)$ python setup.py install
    (venv)$ cd ..

Ausführen::

    (venv)$ python headless_example.py

sowie::

    (venv)$ python pyglet_example.py

(Pfeiltasten, um das rote Quadrat zu bewegen, Fenster schließen mit `ESC`.)

.. _pycologne: http://pycologne.de/
.. _esper: https://github.com/benmoran56/esper
.. _pyglet: http://pyglet.org
