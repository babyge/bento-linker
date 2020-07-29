from .. import outputs
from ..box import Fn
import io
import textwrap
import itertools as it

@outputs.output
class HOutput(outputs.Output):
    """
    Name of header file to generate containing the imported functions.
    """
    __argname__ = "h"
    __arghelp__ = __doc__

    def __init__(self, path=None):
        super().__init__(path)

        self.includes = outputs.OutputField(self)
        self.decls = outputs.OutputField(self)

    @staticmethod
    def repr_arg(arg, name=None):
        name = name if name is not None else arg.name
        return ''.join([
            'const ' if arg.isconst() else '',
            'void'      if arg.prim() == 'u8' and arg.isptr() else
            'char'      if arg.prim() == 'i8' and arg.isptr() else
            'bool'      if arg.prim() == 'bool' else
            'int32_t'   if arg.prim() == 'err32' else
            'int64_t'   if arg.prim() == 'err64' else
            'ssize_t'   if arg.prim() == 'errsize' else
            'int'       if arg.prim().startswith('err') else
            'ssize_t'   if arg.prim() == 'isize' else
            'size_t'    if arg.prim() == 'usize' else
            'int%s_t'  % arg.prim()[1:] if arg.prim().startswith('i') else
            'uint%s_t' % arg.prim()[1:] if arg.prim().startswith('u') else
            'float'     if arg.prim() == 'f32' else
            'double'    if arg.prim() == 'f64' else
            '???',
            ' ' if name else '',
            '*' if arg.isptr() else '',
            name if name else ''])

    @staticmethod
    def repr_fn(fn, name=None, attrs=[]):
        return ''.join(it.chain(
            (attr + ('\n' if attr.startswith('__') else ' ')
                for attr in it.chain(
                    (['__attribute__((noreturn))']
                        if fn.isnoreturn() and (
                            name is None or '*' not in name) else
                        []) +
                    attrs)), [
            '%s ' % HOutput.repr_arg(fn.rets[0], '') if fn.rets else
            'void ',
            name if name is not None else fn.alias,
            '(',
            ', '.join(HOutput.repr_arg(arg, name)
                for arg, name in zip(fn.args, fn.argnames()))
            if fn.args else
            'void',
            ')']))

    @staticmethod
    def repr_fnptr(fn, name=None, attrs=[]):
        return HOutput.repr_fn(fn,
            '(*%s)' % (name if name is not None else fn.alias),
            attrs)

    def box(self, box):
        super().box(box)
        self.pushattrs(gaurd='__BOX_%(BOX)s_H')

    def build_prologue(self, box):
        # always need standard types
        self.includes.append("<stdint.h>")
        self.includes.append("<stdbool.h>")
        self.includes.append("<sys/types.h>")

        for i, import_ in enumerate(
                import_.postbound() for import_ in box.imports
                if import_.source == box):
            if i == 0:
                self.decls.append('//// box imports ////')
            self.decls.append('%(fn)s;',
                fn=self.repr_fn(import_),
                doc=import_.doc)

        for i, export in enumerate(
                export.prebound() for export in box.exports
                if export.source == box):
            if i == 0:
                self.decls.append('//// box exports ////')
            self.decls.append('%(fn)s;',
                fn=self.repr_fn(export, attrs=['extern']),
                doc=export.doc)

        # functions we can expect from runtimes
        self.decls.append('//// box hooks ////')
        for subbox in box.boxes:
            with self.pushattrs(box=subbox.name):
                # TODO move these?
                self.decls.append(
                    'int __box_%(box)s_init(void);',
                    doc='Initialize box %(box)s. Resets the box to its '
                        'initial state if already initialized.')
                self.decls.append(
                    'int __box_%(box)s_clobber(void);',
                    doc='Mark the box %(box)s as needing to be reinitialized.')
                self.decls.append(
                    'void *__box_%(box)s_push(size_t size);',
                    doc='Allocate size bytes on the box\'s data stack. May '
                        'return NULL if a stack overflow would occur.')
                self.decls.append(
                    'void __box_%(box)s_pop(size_t size);',
                    doc='Deallocate size bytes on the box\'s data stack.')

    def getvalue(self):
        self.seek(0)
        self.printf('////// AUTOGENERATED //////')
        self.printf('#ifndef %(gaurd)s')
        self.printf('#define %(gaurd)s')

        includes = set()
        for include in self.includes:
            include = str(include)
            if not (include.startswith('"') or include.startswith('<')):
                include = '"%s"' % include
            includes.add(include)
        for include in sorted(includes):
            self.printf('#include %(include)s', include=include)

        self.print()

        for decl in self.decls:
            if 'doc' in decl:
                for line in textwrap.wrap(decl['doc'], width=78-3):
                    self.print('// %s' % line)
            self.print(decl.getvalue().strip())
            self.print()

        self.printf('#endif')

        return super().getvalue()
