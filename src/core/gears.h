#ifndef _GEARS_H_
#define _GEARS_H_

#include <cairo.h>
#include <X11/Xutil.h>

#define N_FILTER 25
#define DEFAULT_FONT "WenQuanYi Micro Hei"
#define benchmark  20

struct device;
struct framebuffer;
struct slide;

static double gear1_rotation = 0.35;
static double gear2_rotation = 0.33;
static double gear3_rotation = 0.50;

struct framebuffer {
    struct device *device;

    cairo_surface_t *surface;

    void (*show) (struct framebuffer *);
    void (*destroy) (struct framebuffer *);
};

struct device {
    const char *name;
    struct framebuffer * (*get_framebuffer) (struct device *);
    cairo_surface_t *scanout;
    int width, height;
};

struct xlib_device
{
    struct device base;
    struct framebuffer fb;

    Display *display;
    Window drawable;
    Pixmap pixmap;
};

double gear_fps();
#endif