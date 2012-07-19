from django.conf.urls.defaults import *

#...

import face4django
up = patterns( '', *face4django.urls )
urlpatterns += patterns( '', ('^facer/', include( up)))
