#ifndef _LSHW_H_
#define _LSHW_H_

class lshw
{
public:
    lshw();
    virtual ~lshw();

    void scan_device();
    string get_xml();

private:
    hwNode *computer;
};

char *degree_sign();

#endif