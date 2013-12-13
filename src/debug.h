/*
Copyright 2013 Michael Curran <mick@nvaccess.org>.
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License version 2.1, as published by
    the Free Software Foundation.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
This license can be found at:
http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html
*/

#ifndef AUDIOSCREEN_DEBUG_H
#define AUDIOSCREEN_DEBUG_H

#include <iostream>

#define DEBUG(msg) cerr<<__FILE__<<" line "<<__LINE__<<" in "<<__FUNCTION__<<":"<<endl<<msg<<endl

#endif
