#include "osutils.h"
#include <sstream>
#include <iomanip>
#include <stack>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <dirent.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>
#include <ctype.h>
#include <stdio.h>
#include <errno.h>
#include <wchar.h>
#include <sys/utsname.h>
#ifndef MINOR
#include <linux/kdev_t.h>
#endif


using namespace std;

static stack < string > dirs;

bool pushd(const string & dir)
{
    string curdir = pwd();

    if(dir == "")
    {
        if(dirs.size() == 0)
            return true;

        if(chdir(dirs.top().c_str()) == 0)
        {
            dirs.pop();
            dirs.push(curdir);
            return true;
        }
        else
            return false;
    }

    if(chdir(dir.c_str()) == 0)
    {
        dirs.push(curdir);
        return true;
    }
    else
        return false;
}

string popd()
{
    string curdir = pwd();

    if(dirs.size() == 0)
        return curdir;

    if(chdir(dirs.top().c_str()) == 0)
        dirs.pop();

    return curdir;
}

string pwd()
{
    char curdir[PATH_MAX + 1];

    if(getcwd(curdir, sizeof(curdir)))
        return string(curdir);
    else
        return "";
}

size_t splitlines(const string & s,
        vector < string > &lines,
        char separator)
{
    size_t i = 0, j = 0;
    size_t count = 0;

    lines.clear();

    while((j < s.length()) && ((i = s.find(separator, j)) != string::npos))
    {
        lines.push_back(s.substr(j, i - j));
        count++;
        i++;
        j = i;
    }
    if(j < s.length())
    {
        lines.push_back(s.substr(j));
        count++;
    }

    return count;
}

bool exists(const string & path)
{
    return access(path.c_str(), F_OK) == 0;
}

bool loadfile(const string & file,
        vector < string > &list)
{
    char buffer[1024];
    string buffer_str = "";
    size_t count = 0;
    int fd = open(file.c_str(), O_RDONLY);

    if(fd < 0)
        return false;

    while((count = read(fd, buffer, sizeof(buffer))) > 0)
        buffer_str += string(buffer, count);

    splitlines(buffer_str, list);

    close(fd);

    return true;
}

int selectdir(const struct dirent *d)
{
    struct stat buf;

    if(d->d_name[0] == '.')
        return 0;

    if(lstat(d->d_name, &buf) != 0)
        return 0;

    return S_ISDIR(buf.st_mode);
}

int selectlink(const struct dirent *d)
{
    struct stat buf;

    if(d->d_name[0] == '.')
        return 0;

    if(lstat(d->d_name, &buf) != 0)
        return 0;

    return S_ISLNK(buf.st_mode);
}

int selectfile(const struct dirent *d)
{
    struct stat buf;

    if(d->d_name[0] == '.')
        return 0;

    if(lstat(d->d_name, &buf) != 0)
        return 0;

    return S_ISREG(buf.st_mode);
}

string get_devid(const string & name)
{
    struct stat buf;

    if((stat(name.c_str(), &buf) == 0) && (S_ISBLK(buf.st_mode) || S_ISCHR(buf.st_mode)))
    {
        char devid[80];

        snprintf(devid, sizeof(devid), "%u:%u", (unsigned int) MAJOR(buf.st_rdev), (unsigned int) MINOR(buf.st_rdev));
        return string(devid);
    }
    else
        return "";
}

bool samefile(const string & path1, const string & path2)
{
    struct stat stat1;
    struct stat stat2;

    if(stat(path1.c_str(), &stat1) != 0)
        return false;
    if(stat(path2.c_str(), &stat2) != 0)
        return false;

    return(stat1.st_dev == stat2.st_dev) && (stat1.st_ino == stat2.st_ino);
}

string uppercase(const string & s)
{
    string result;

    for(unsigned int i = 0; i < s.length(); i++)
        result += toupper(s[i]);

    return result;
}

string lowercase(const string & s)
{
    string result;

    for(unsigned int i = 0; i < s.length(); i++)
        result += tolower(s[i]);

    return result;
}

string tostring(unsigned long long n)
{
    char buffer[80];

    snprintf(buffer, sizeof(buffer), "%lld", n);

    return string(buffer);
}

string tohex(unsigned long long n)
{
    char buffer[80];

    snprintf(buffer, sizeof(buffer), "%.4llX", n);

    return string(buffer);
}

bool matches(const string & s, const string & pattern, int cflags)
{
    regex_t r;
    bool result = false;

    if(regcomp(&r, pattern.c_str(), REG_EXTENDED | REG_NOSUB | cflags) != 0)
        return false;

    result = (regexec(&r, s.c_str(), 0, NULL, 0) == 0);

    regfree(&r);

    return result;
}

string readlink(const string & path)
{
    char buffer[PATH_MAX + 1];

    memset(buffer, 0, sizeof(buffer));
    if(readlink(path.c_str(), buffer, sizeof(buffer) - 1) > 0)
        return string(buffer);
    else
        return path;
}

string realpath(const string & path)
{
    char buffer[PATH_MAX + 1];

    memset(buffer, 0, sizeof(buffer));
    if(realpath(path.c_str(), buffer))
        return string(buffer);
    else
        return path;
}

string spaces(unsigned int count, const string & space)
{
    string result = "";
    while(count-- > 0)
        result += space;

    return result;
}

string escape(const string & s)
{
    string result = "";

    for(unsigned int i = 0; i < s.length(); i++)
        // #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
        if(s[i] == 0x9
                || s[i] == 0xA
                || s[i] == 0xD
                || s[i] >= 0x20)
            switch(s[i])
            {
                case '<':
                    result += "&lt;";
                    break;
                case '>':
                    result += "&gt;";
                    break;
                case '&':
                    result += "&amp;";
                    break;
                case '"':
                    result += "&quot;";
                    break;
                default:
                    result += s[i];
            }

    return result;
}

string escapecomment(const string & s)
{
    string result = "";
    char previous = 0;

    for(unsigned int i = 0; i < s.length(); i++)
        if(!(previous == '-' && s[i] == '-'))
        {
            result += s[i];
            previous = s[i];
        }

    return result;
}

int open_dev(dev_t dev, const string & name)
{
    static const char *paths[] = {
        "/usr/tmp", "/var/tmp", "/var/run", "/dev", "/tmp", NULL
    };
    char const **p;
    char fn[64];
    int fd;

    for(p = paths; *p; p++)
    {
        if(name == "")
            snprintf(fn, sizeof(fn), "%s/lshw-%d", *p, getpid());
        else
            snprintf(fn, sizeof(fn), "%s", name.c_str());
        if((mknod(fn, (S_IFCHR | S_IREAD), dev) == 0) || (errno == EEXIST))
        {
            fd = open(fn, O_RDONLY);
            if(name == "") unlink(fn);
            if(fd >= 0)
                return fd;
        }
    }
    return -1;
}

// U+FFFD replacement character
#define REPLACEMENT  "\357\277\275"

string utf8_sanitize(const string & s)
{
    unsigned int i = 0;
    unsigned int remaining = 0;
    string result = "";
    string emit = "";
    unsigned char c = 0;

    while(i < s.length())
    {
        c = s[i];
        switch(remaining)
        {
            case 3:
            case 2:
            case 1:
                if((0x80 <= c) && (c <= 0xbf))
                {
                    emit += s[i];
                    remaining--;
                }
                else // invalid sequence (truncated)
                {
                    emit = REPLACEMENT;
                    emit += s[i];
                    remaining = 0;
                }
                break;

            case 0:
                result += emit;
                emit = "";

                if(c <= 0x7f)
                    emit = s[i];
                else
                    if((0xc2 <= c) && (c <= 0xdf)) // start 2-byte sequence
                {
                    remaining = 1;
                    emit = s[i];
                }
                else
                    if((0xe0 <= c) && (c <= 0xef)) // start 3-byte sequence
                {
                    remaining = 2;
                    emit = s[i];
                }
                else
                    if((0xf0 <= c) && (c <= 0xf4)) // start 4-byte sequence
                {
                    remaining = 3;
                    emit = s[i];
                }
                else
                    emit = REPLACEMENT; // invalid character

                break;
        }

        i++;
    }

    if(remaining == 0)
        result += emit;

    return result;
}

string platform()
{
    string p = "";
    struct utsname u;

#ifdef __i386__
    p = "i386";
#endif

    if(uname(&u) != 0)
        return p;
    else
        return p + (p != "" ? "/" : "") + string(u.machine);
}
