////// AUTOGENERATED //////
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
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

//// box exports ////

extern int box3_add2(int32_t a0, int32_t a1);

extern int box3_hello(void);

//// box hooks ////

// Forcefully terminate the current box with the specified error. The box can
// not be called again after this without a new init. Does not return.
__attribute__((noreturn))
void __box_abort(int err);

// Write to stdout if provided by superbox. If not provided, this function is
// still available for linking, but does nothing. Returns 0 on success,
// negative error code on failure.
ssize_t __box_write(int32_t fd, void *buffer, size_t size);

//// __box_abort glue ////

__attribute__((used, noreturn))
void __wrap_abort(void) {
    __box_abort(-1);
}

#ifdef __GNUC__
__attribute__((noreturn))
void __assert_func(const char *file, int line,
        const char *func, const char *expr) {
    printf("%s:%d: assertion \"%s\" failed\n", file, line, expr);
    __box_abort(-1);
}

__attribute__((noreturn))
void _exit(int returncode) {
    __box_abort(-returncode);
}
#endif

//// __box_write glue ////

ssize_t __box_cbprintf(
        ssize_t (*write)(void *ctx, const void *buf, size_t size), void *ctx,
        const char *format, va_list args) {
    const char *p = format;
    ssize_t res = 0;
    while (true) {
        // first consume everything until a '%'
        const char *np = strchr(p, '%');
        size_t skip = np ? np - p : strlen(p);

        if (skip > 0) {
            ssize_t nres = write(ctx, p, skip);
            if (nres < 0) {
                return nres;
            }
            res += nres;
        }

        // hit end of string?
        if (!np) {
            return res;
        }

        // format parser
        p = np;
        bool zero_justify = false;
        bool left_justify = false;
        bool precision_mode = false;
        size_t width = 0;
        size_t precision = 0;

        char mode = 'c';
        uint32_t value = 0;
        size_t size = 0;

        for (;; np++) {
            if (np[1] >= '0' && np[1] <= '9') {
                // precision/width
                if (precision_mode) {
                    precision = precision*10 + (np[1]-'0');
                } else if (np[1] > '0' || width > 0) {
                    width = width*10 + (np[1]-'0');
                } else {
                    zero_justify = true;
                }

            } else if (np[1] == '*') {
                // dynamic precision/width
                if (precision_mode) {
                    precision = va_arg(args, size_t);
                } else {
                    width = va_arg(args, size_t);
                }

            } else if (np[1] == '.') {
                // switch mode
                precision_mode = true;

            } else if (np[1] == '-') {
                // left-justify
                left_justify = true;

            } else if (np[1] == '%') {
                // single '%'
                mode = 'c';
                value = '%';
                size = 1;
                break;

            } else if (np[1] == 'c') {
                // char
                mode = 'c';
                value = va_arg(args, int);
                size = 1;
                break;

            } else if (np[1] == 's') {
                // string
                mode = 's';
                const char *s = va_arg(args, const char *);
                value = (uint32_t)s;
                // find size, don't allow overruns
                size = 0;
                while (s[size] && (precision == 0 || size < precision)) {
                    size += 1;
                }
                break;

            } else if (np[1] == 'd' || np[1] == 'i') {
                // signed decimal number
                mode = 'd';
                int32_t d = va_arg(args, int32_t);
                value = (uint32_t)d;
                size = 0;
                if (d < 0) {
                    size += 1;
                    d = -d;
                }
                for (uint32_t t = d; t > 0; t /= 10) {
                    size += 1;
                }
                if (size == 0) {
                    size += 1;
                }
                break;

            } else if (np[1] == 'u') {
                // unsigned decimal number
                mode = 'u';
                value = va_arg(args, uint32_t);
                size = 0;
                for (uint32_t t = value; t > 0; t /= 10) {
                    size += 1;
                }
                if (size == 0) {
                    size += 1;
                }
                break;

            } else if (np[1] >= ' ' && np[1] <= '?') {
                // unknown modifier? skip

            } else {
                // hex or unknown character, terminate

                // make it prettier for pointers
                if (!(np[1] == 'x' || np[1] == 'X')) {
                    zero_justify = true;
                    width = 2*sizeof(void*);
                }

                // hexadecimal number
                mode = 'x';
                value = va_arg(args, uint32_t);
                size = 0;
                for (uint32_t t = value; t > 0; t /= 16) {
                    size += 1;
                }
                if (size == 0) {
                    size += 1;
                }
                break;
            }
        }

        // consume the format
        p = np+2;

        // format printing
        if (!left_justify) {
            for (ssize_t i = 0; i < (ssize_t)width-(ssize_t)size; i++) {
                char c = (zero_justify) ? '0' : ' ';
                ssize_t nres = write(ctx, &c, 1);
                if (nres < 0) {
                    return nres;
                }
                res += nres;
            }
        }

        if (mode == 'c') {
            ssize_t nres = write(ctx, &value, 1);
            if (nres < 0) {
                return nres;
            }
            res += nres;
        } else if (mode == 's') {
            ssize_t nres = write(ctx, (const char*)(uintptr_t)value, size);
            if (nres < 0) {
                return nres;
            }
            res += nres;
        } else if (mode == 'x') {
            for (ssize_t i = size-1; i >= 0; i--) {
                uint32_t digit = (value >> (4*i)) & 0xf;

                char c = ((digit >= 10) ? ('a'-10) : '0') + digit;
                ssize_t nres = write(ctx, &c, 1);
                if (nres < 0) {
                    return nres;
                }
                res += nres;
            }
        } else if (mode == 'd' || mode == 'u') {
            ssize_t i = size-1;

            if (mode == 'd' && (int32_t)value < 0) {
                ssize_t nres = write(ctx, "-", 1);
                if (nres < 0) {
                    return nres;
                }
                res += nres;

                value = -value;
                i -= 1;
            }

            for (; i >= 0; i--) {
                uint32_t temp = value;
                for (int j = 0; j < i; j++) {
                    temp /= 10;
                }
                uint32_t digit = temp % 10;

                char c = '0' + digit;
                ssize_t nres = write(ctx, &c, 1);
                if (nres < 0) {
                    return nres;
                }
                res += nres;
            }
        }
        
        if (left_justify) {
            for (ssize_t i = 0; i < (ssize_t)width-(ssize_t)size; i++) {
                char c = ' ';
                ssize_t nres = write(ctx, &c, 1);
                if (nres < 0) {
                    return nres;
                }
                res += nres;
            }
        }
    }
}

static ssize_t __box_vprintf_write(void *ctx, const void *buf, size_t size) {
    // TODO hm, not const?
    return __box_write((int32_t)ctx, (void *)buf, size);
}

__attribute__((used))
ssize_t __wrap_vprintf(const char *format, va_list args) {
    return __box_cbprintf(__box_vprintf_write, (void*)1, format, args);
}

__attribute__((used))
ssize_t __wrap_printf(const char *format, ...) {
    va_list args;
    va_start(args, format);
    ssize_t res = __wrap_vprintf(format, args);
    va_end(args);
    return res;
}

__attribute__((used))
ssize_t __wrap_vfprintf(FILE *f, const char *format, va_list args) {
    int32_t fd = (f == stdout) ? 1 : 2;
    return __box_cbprintf(__box_vprintf_write, (void*)fd, format, args);
}

__attribute__((used))
ssize_t __wrap_fprintf(FILE *f, const char *format, ...) {
    va_list args;
    va_start(args, format);
    ssize_t res = __wrap_vfprintf(f, format, args);
    va_end(args);
    return res;
}

__attribute__((used))
int __wrap_fflush(FILE *f) {
    // do nothing currently
    return 0;
}

#ifdef __GNUC__
int _write(int handle, char *buffer, int size) {
    return __box_write(handle, (uint8_t*)buffer, size);
}
#endif

//// jumptable implementation ////

int32_t __box_init(void) {
    // zero bss
    extern uint32_t __bss_start;
    extern uint32_t __bss_end;
    for (uint32_t *d = &__bss_start; d < &__bss_end; d++) {
        *d = 0;
    }

    // load data
    extern uint32_t __data_init_start;
    extern uint32_t __data_start;
    extern uint32_t __data_end;
    const uint32_t *s = &__data_init_start;
    for (uint32_t *d = &__data_start; d < &__data_end; d++) {
        *d = *s++;
    }

    // init libc
    extern void __libc_init_array(void);
    __libc_init_array();

    return 0;
}

extern uint32_t __stack_end;

// box-side jumptable
__attribute__((section(".jumptable")))
__attribute__((used))
const uint32_t __box_box3_jumptable[] = {
    (uint32_t)&__stack_end,
    (uint32_t)__box_init,
    (uint32_t)__box_abort,
    (uint32_t)__box_write,
    (uint32_t)box3_add2,
    (uint32_t)box3_hello,
};

