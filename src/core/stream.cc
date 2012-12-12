#include <stdio.h>
#include <sys/time.h>
#include "stream.h"

/*
 * STREAM
 */

double stream_triad()
{
    register int j, k;
    double scalar, t, times[NTIMES];

#pragma omp parallel for //将一个循环并行执行
    for(j = 0; j < N; j++)
    {
        a[j] = 1.0;
        b[j] = 2.0;
        c[j] = 0.0;
    }

    t = mysecond();

#pragma omp parallel for
    for(j = 0; j < N; j++)
        a[j] = 2.0E0 * a[j];

    t = 1.0E6 * (mysecond() - t);

    scalar = 3.0;
    for(k = 0; k < NTIMES; k++)
    {
        times[k] = mysecond();
        tuned_STREAM_Triad(scalar);
        times[k] = mysecond() - times[k];
    }

    for(k = 1; k < NTIMES; k++)
    {
        mintime = MIN(mintime, times[k]);
    }
    //printf("%.2f \n", 1.0E-06 * bytes / mintime);

    return 1.0E-06 * bytes / mintime;
}

double mysecond()
{
    struct timeval tp;
    struct timezone tzp;
    int i;

    i = gettimeofday(&tp, &tzp);
    return( (double) tp.tv_sec + (double) tp.tv_usec * 1.e-6);
}

void tuned_STREAM_Triad(double scalar)
{
    int j;
#pragma omp parallel for
    for(j = 0; j < N; j++)
        a[j] = b[j] + scalar * c[j];
}
