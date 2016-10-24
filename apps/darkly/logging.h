#ifndef _LOGGING_GUARD
#define _LOGGING_GUARD
#include <stdio.h>
#include <sys/time.h>
#include <time.h>

#define INFOLEVEL 1
#define DEBUGLEVEL 2
#define INFO(log) logging(TAG, log, INFOLEVEL)
#define DEBUG(log) logging(TAG, log, DEBUGLEVEL)
void logging(const char *TAG, const char *log, unsigned int lev) {
  const char *fmt = "%10.6f:%s:%s:native:%s\n";
  const char *level;
  switch (lev) {
    case INFOLEVEL:
      level = "INFO";
      break;
    case DEBUGLEVEL:
      level = "DEBUG";
      break;
    default:
      level = "LOG";
      break;
  }
  struct timeval micro;
  gettimeofday(&micro, NULL);
  time_t t;
  time(&t);
  double f = t + micro.tv_usec / 1000000.0;
  fprintf(stderr, fmt, f, level, TAG, log);
}
#endif
