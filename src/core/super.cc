#include "super.h"
/*矩形积分法示π
 * f(x) = 4/(1+x*x)
 * pi = 1/N(f((i-0.5)/N)+...)
 */

double super_pi()
{
    long int i;
    double x, pi, sum, step, time = 0.0;
    struct timeval start, end;

    gettimeofday(&start, NULL); //开始计时
    step = 1.0 / NUM;

#pragma omp parallel for reduction(+:sum) private(x)
    for(i = 1; i < NUM; i++)
    {
        x = (i - 0.5) * step;
        sum += 4.0 / (1.0 + x * x);
    }
    pi = step*sum;

    gettimeofday(&end, NULL); //结束计时
    time = 1000000 * (end.tv_sec - start.tv_sec) + end.tv_usec - start.tv_usec;

    return time / 1000000;
    //printf("pi == %.15f time == %fsec\n", pi, time/1000000);
}
