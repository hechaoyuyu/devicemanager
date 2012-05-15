#ifndef _STREAM_H_
#define _STREAM_H_

#ifndef N
#define N 2000000
#endif
#ifndef NTIMES
#define NTIMES	10
#endif
#ifndef OFFSET
#define OFFSET	0
#endif

#ifndef MIN
#define MIN(x,y) ((x)<(y)?(x):(y))
#endif
#ifndef MAX
#define MAX(x,y) ((x)>(y)?(x):(y))
#endif

#include <float.h>

static double a[N + OFFSET], b[N + OFFSET], c[N + OFFSET];
static double avgtime = 0, mintime = FLT_MAX;
static double bytes = 3 * sizeof (double) * N;

double mysecond();
void tuned_STREAM_Triad(double);
double stream_triad();
#endif