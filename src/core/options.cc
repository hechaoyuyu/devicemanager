/*
 * options.cc
 *
 * This module handles global options passed on the command-line.
 *
 */

#include "options.h"
#include "osutils.h"

#include <set>
#include <vector>
#include <string>
#include <map>

#include <stdlib.h>

using namespace std;


static set < string > disabled_tests;
static set < string > visible_classes;
static map < string, string > aliases;

static string getcname(const char * aname)
{
    if(aliases.find(lowercase(aname)) != aliases.end())
        return lowercase(aliases[lowercase(aname)]);
    else
        return lowercase(aname);
}

bool enabled(const char *option)
{
    return !(disabled(lowercase(option).c_str()));
}

bool disabled(const char *option)
{
    return disabled_tests.find(lowercase(option)) != disabled_tests.end();
}

void enable(const char *option)
{
    if(!disabled(option))
        return;

    disabled_tests.erase(lowercase(option));
}

void disable(const char *option)
{
    disabled_tests.insert(lowercase(option));
}

bool visible(const char *c)
{
    if(visible_classes.size() == 0)
        return true;
    return visible_classes.find(getcname(c)) != visible_classes.end();
}
