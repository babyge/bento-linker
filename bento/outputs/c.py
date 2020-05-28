from .. import outputs
from ..box import Fn
from .h import buildinclude, buildfn, HOutput
import io
import textwrap

@outputs.output
class COutput(outputs.HOutput):
    """
    Name of source file to target for building a jumptable.
    """
    __argname__ = "c"
    __arghelp__ = __doc__

    def __init__(self, path=None):
        super().__init__(path)
        self.includes = outputs.OutputField(self, rules={str: buildinclude})
        self.decls = outputs.OutputField(self, rules={Fn: buildfn})

    def build(self, box):
        outputs.Output.build(self, box)
        self.write('////// AUTOGENERATED //////\n')
        includes = set()
        for include in self.includes:
            includes.add(include.getvalue())
        for include in sorted(includes):
            self.write('#include %s\n' % include)
        self.write('\n')

        for decl in self.decls:
            if decl.getvalue().startswith(4*'/'):
                self.write('\n')
            if decl.get('doc', None) is not None:
                for line in textwrap.wrap(decl['doc'] % decl, width=77):
                    self.write('// %s\n' % line)
            self.write(decl.getvalue().strip())
            self.write('\n\n')