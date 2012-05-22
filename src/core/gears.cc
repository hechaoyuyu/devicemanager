#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdio.h>
#include <cairo.h>
#include <cairo-xlib.h>
#include <sys/time.h>
#include "gears.h"

static void gear(cairo_t *cr, double inner_radius, double outer_radius, int teeth, double tooth_depth)
{
    int i;
    double r0, r1, r2;
    double angle, da;

    r0 = inner_radius;
    r1 = outer_radius - tooth_depth / 2.0;
    r2 = outer_radius + tooth_depth / 2.0;

    da = 2.0 * M_PI / (double) teeth / 4.0;

    cairo_new_path(cr);

    angle = 0.0;
    cairo_move_to(cr, r1 * cos(angle + 3 * da), r1 * sin(angle + 3 * da));

    for(i = 1; i <= teeth; i++)
    {
        angle = i * 2.0 * M_PI / (double) teeth;

        cairo_line_to(cr, r1 * cos(angle), r1 * sin(angle));
        cairo_line_to(cr, r2 * cos(angle + da), r2 * sin(angle + da));
        cairo_line_to(cr, r2 * cos(angle + 2 * da), r2 * sin(angle + 2 * da));

        if(i < teeth)
            cairo_line_to(cr,
                r1 * cos(angle + 3 * da),
                r1 * sin(angle + 3 * da));
    }

    cairo_close_path(cr);

    cairo_new_sub_path(cr);
    cairo_arc_negative(cr, 0, 0, r0, 2 * M_PI, 0);
}

static void gears_render(cairo_t *cr, int w, int h)
{
    cairo_set_source_rgba(cr, 0.75, 0.75, 0.75, 1.0);
    cairo_set_line_width(cr, 1.0);

    cairo_save(cr);
    cairo_scale(cr, (double) w / 512.0, (double) h / 512.0);

    cairo_save(cr);
    cairo_translate(cr, 170.0, 330.0);
    cairo_rotate(cr, gear1_rotation);

    gear(cr, 30.0, 120.0, 20, 20.0);
    cairo_set_source_rgb(cr, 0.75, 0.45, 0.45);
    cairo_set_antialias(cr, CAIRO_ANTIALIAS_NONE);
    cairo_fill_preserve(cr);
    cairo_set_source_rgb(cr, 0.25, 0.15, 0.15);
    cairo_set_antialias(cr, CAIRO_ANTIALIAS_DEFAULT);
    cairo_stroke(cr);
    cairo_restore(cr);

    cairo_save(cr);
    cairo_translate(cr, 369.0, 330.0);
    cairo_rotate(cr, gear2_rotation);

    gear(cr, 15.0, 75.0, 12, 20.0);
    cairo_set_source_rgb(cr, 0.45, 0.75, 0.45);
    cairo_set_antialias(cr, CAIRO_ANTIALIAS_NONE);
    cairo_fill_preserve(cr);
    cairo_set_source_rgb(cr, 0.15, 0.25, 0.15);
    cairo_set_antialias(cr, CAIRO_ANTIALIAS_DEFAULT);
    cairo_stroke(cr);
    cairo_restore(cr);

    cairo_save(cr);
    cairo_translate(cr, 170.0, 116.0);
    cairo_rotate(cr, gear3_rotation);

    gear(cr, 20.0, 90.0, 14, 20.0);
    cairo_set_source_rgb(cr, 0.45, 0.45, 0.75);
    cairo_set_antialias(cr, CAIRO_ANTIALIAS_NONE);
    cairo_fill_preserve(cr);
    cairo_set_antialias(cr, CAIRO_ANTIALIAS_DEFAULT);
    cairo_set_source_rgb(cr, 0.15, 0.15, 0.25);
    cairo_stroke(cr);
    cairo_restore(cr);

    gear1_rotation += 0.01;
    gear2_rotation -= (0.01 * (20.0 / 12.0));
    gear3_rotation -= (0.01 * (20.0 / 14.0));
}

static void destroy(struct framebuffer *fb)
{
    //cairo_surface_destroy(fb->surface);
}

static void show(struct framebuffer *fb)
{
    struct xlib_device *device = (struct xlib_device *) fb->device;
    cairo_t *cr;

    cr = cairo_create(device->base.scanout);
    cairo_set_source_surface(cr, fb->surface, 0, 0);
    cairo_paint(cr);
    cairo_destroy(cr);

    if(1)
    {
        XImage *image = XGetImage(device->display,
                device->pixmap,
                0, 0, 1, 1,
                AllPlanes, ZPixmap
                );
        if(image)
            XDestroyImage(image);
    }
}

static struct framebuffer * get_fb(struct device *abstract_device)
{
    struct xlib_device *device = (struct xlib_device *) abstract_device;
    return &device->fb;
}

Display *dpy;

struct device * xlib_open()
{
    struct xlib_device *device;
    Screen *scr;
    int screen;
    XSetWindowAttributes attr;

    dpy = XOpenDisplay(NULL);
    if(dpy == NULL)
        return NULL;

    device = (xlib_device *) malloc(sizeof(struct xlib_device));
    device->base.name = "设备管理器";
    device->base.get_framebuffer = get_fb;
    device->display = dpy;

    screen = DefaultScreen(dpy);
    scr = XScreenOfDisplay(dpy, screen);
    device->base.width = WidthOfScreen(scr);
    device->base.height = HeightOfScreen(scr);

    attr.override_redirect = True;
    device->drawable = XCreateWindow(dpy, DefaultRootWindow(dpy),
            0, 0,
            device->base.width, device->base.height, 0,
            DefaultDepth(dpy, screen),
            InputOutput,
            DefaultVisual(dpy, screen),
            CWOverrideRedirect, &attr
            );
    XMapWindow(dpy, device->drawable);

    device->base.scanout = cairo_xlib_surface_create(dpy, device->drawable,
            DefaultVisual(dpy, screen),
            device->base.width, device->base.height);

    device->pixmap = XCreatePixmap(dpy, device->drawable,
            device->base.width, device->base.height,
            DefaultDepth(dpy, screen));
    device->fb.surface = cairo_xlib_surface_create(dpy, device->pixmap,
            DefaultVisual(dpy, screen),
            device->base.width, device->base.height);

    device->fb.device = &device->base;
    device->fb.show = show;
    device->fb.destroy = destroy;

    return &device->base;
}

struct device *device_open()
{
    struct device *device = 0;

    device = xlib_open();
    if(device == 0)
    {
        fprintf(stderr, "Failed to open a drawing device\n");
        exit(1);
    }

    return device;
}

void fps_draw(cairo_t *cr, const char *name, const int frame, const double delta)
{
    cairo_text_extents_t extents;
    char buf[180];

    cairo_select_font_face(cr, DEFAULT_FONT, CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_BOLD);
    snprintf(buf, sizeof(buf), "%s: %.1f fps, 剩余时间: %.2fs", name, frame / delta, benchmark - delta);
    cairo_set_font_size(cr, 10);
    cairo_text_extents(cr, buf, &extents);

    cairo_set_operator(cr, CAIRO_OPERATOR_OVER);

    cairo_rectangle(cr, 4 - 1, 4 - 1, extents.width + 2, extents.height + 2);
    cairo_set_source_rgba(cr, .0, .0, .0, .5);
    cairo_fill(cr);

    cairo_move_to(cr, 4 - extents.x_bearing, 4 - extents.y_bearing);
    cairo_set_source_rgb(cr, .95, .95, .95);
    cairo_show_text(cr, buf);
}

//int main()

double gear_fps()
{
    struct device *device;
    struct timeval start, last_tty, last_fps, now;

    double delta, fps;
    int frame = 0;

    device = device_open();

    gettimeofday(&start, 0);
    now = last_tty = last_fps = start;

    do
    {
        struct framebuffer *fb = device->get_framebuffer(device);
        cairo_t *cr;

        cr = cairo_create(fb->surface);

        cairo_set_source_rgb(cr, 1.0, 1.0, 1.0);
        cairo_set_operator(cr, CAIRO_OPERATOR_SOURCE);
        cairo_paint(cr);
        cairo_set_operator(cr, CAIRO_OPERATOR_OVER);

        gears_render(cr, device->width, device->height);

        gettimeofday(&now, NULL);

        frame++;
        delta = now.tv_sec - start.tv_sec;
        delta += (now.tv_usec - start.tv_usec)*1e-6;

        fps_draw(cr, device->name, frame, delta);

        cairo_destroy(cr);
        fb->show(fb);
        fb->destroy(fb);

        if(delta > benchmark)
        {
            fps = frame / delta;
            //printf("fps: %.2f \n", fps);
            break;
        }

    }
    while(1);

    //XDestroyWindow(display, window);
    XCloseDisplay(dpy);

    return fps;
}