////// AUTOGENERATED //////
#ifndef __BOX_SYSTEM_H
#define __BOX_SYSTEM_H
#include <stdbool.h>
#include <stdint.h>
#include <sys/types.h>

//// box error codes ////
enum box_err {
    BOX_ERR_OK               = 0,    // No error
    BOX_ERR_GENERAL          = -1,   // General error
    BOX_ERR_NOBOX            = -8,   // Box format error
    BOX_ERR_AGAIN            = -11,  // Try again
    BOX_ERR_NOMEM            = -12,  // Cannot allocate memory
    BOX_ERR_FAULT            = -14,  // Bad address
    BOX_ERR_BUSY             = -16,  // Device or resource busy
    BOX_ERR_LOOP             = -20,  // Cyclic data structure detected
    BOX_ERR_INVAL            = -22,  // Invalid parameter
    BOX_ERR_TIMEDOUT         = -110, // Timed out
};

//// box imports ////

int box1_add2(int32_t a0, int32_t a1);

int box1_badassert(void);

int box1_badread(void);

int box1_badwrite(void);

int box1_hello(void);

int box1_overflow(void);

//// box exports ////

extern ssize_t __box_write(int32_t a0, void *a1, size_t a2);

//// box hooks ////

// Forcefully terminate the current box with the specified error. The box can
// not be called again after this without a new init. Does not return.
__attribute__((noreturn))
void __box_abort(int err);

// Write to stdout if provided by superbox. If not provided, this function is
// still available for linking, but does nothing. Returns 0 on success,
// negative error code on failure.
ssize_t __box_write(int32_t fd, void *buffer, size_t size);

// Initialize box box1.
int __box_box1_init(void);

// Mark the box box1 as needing to be reinitialized.
int __box_box1_clobber(void);

#endif
