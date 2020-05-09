from .. import outputs
from ..box import Memory
import io
import textwrap

def buildmemory(outf, memory):
    outf.pushattrs(
        memory='%(memory_prefix)s' + memory.name,
        mode=''.join(sorted(memory.mode)),
        addr=memory.addr,
        size=memory.size)
    outf.write('%(MEMORY)-16s (%(MODE)s) : '
        'ORIGIN = %(addr)#010x, '
        'LENGTH = %(size)#010x')

## TODO need access to high-level output?
#def buildstack(stack, outf):
#    outf.pushattrs(mode='rw') # TODO how get mem attr??
#    outf.write('.stack (NOLOAD) : {\n')
#    with outf.pushindent():
#        outf.write('. = ALIGN(8);\n')
#        outf.write('__stack = .;\n')
#        outf.write('. += __stack_min;\n')
#        outf.write('. = ALIGN(8);\n')
#        outf.write('__stack_end = .;\n')
#    outf.write('} > %(mem)s\n')

@outputs.output('sys')
@outputs.output('box')
class ParialLDScriptOutput_(outputs.Output_):
    """
    Name of file to target for a partial linkerscript. This is the minimal
    additions needed for a bento box and should be imported into a traditional
    linkerscript to handle the normal program sections.
    """
    __argname__ = "partial_ldscript_"
    __arghelp__ = __doc__

    def __init__(self, box, path=None,
            symbol_prefix='__',
            section_prefix='.',
            memory_prefix=''):
        super().__init__(box, path)
        self.decls = outputs.OutputField_(self)
        self.memories = outputs.OutputField_(self, {Memory: buildmemory},
            indent=4,
            memory=None,
            mode='rwx',
            addr=0,
            size=0)
        self.sections = outputs.OutputField_(self,
            indent=4,
            section=None,
            memory=None,
            align=4)
        self.pushattrs(
            symbol_prefix=symbol_prefix,
            section_prefix=section_prefix,
            memory_prefix=memory_prefix)

        # create memories + sections for subboxes?
        for subbox in box.boxes:
            ldscript = LDScriptOutput_(subbox,
                symbol_prefix='__box_%(box)s_',
                section_prefix='.box.%(box)s.',
                memory_prefix='box_%(box)s_')
            self.decls.extend(ldscript.decls)
            self.memories.extend(ldscript.memories)
            self.sections.extend(ldscript.sections)
            for memory in ldscript.memories:
                self.decls.append('%(symbol)-16s = '
                    'ORIGIN(%(MEMORY)s);',
                    symbol='%(symbol_prefix)s%(memory)s',
                    memory=memory['memory'])
                self.decls.append('%(symbol)-16s = '
                    'ORIGIN(%(MEMORY)s) + LENGTH(%(MEMORY)s);',
                    symbol='%(symbol_prefix)s%(memory)s_end',
                    memory=memory['memory'])

    def build(self, outf):
        # TODO docs?
        outf.write('/***** AUTOGENERATED *****/\n')
        outf.write('\n')
        if self.decls:
            for decl in self.decls:
                outf.write(decl.getvalue())
                outf.write('\n')
            outf.write('\n')
        if self.memories:
            outf.write('MEMORY {\n')
            # order memories based on address
            for memory in sorted(self.memories, key=lambda m: m['addr']):
                outf.write(memory.getvalue())
                outf.write('\n')
            outf.write('}\n')
            outf.write('\n')
        if self.sections:
            outf.write('SECTIONS {\n')
            # order sections based on memories' address
            sections = self.sections
            for memory in sorted(self.memories, key=lambda m: m['addr']):
                if any(section['memory'] == memory['memory']
                        for section in sections):
                    outf.write('    /* %s sections */\n'
                        % memory['memory'].upper())
                nsections = []
                for section in sections:
                    if section['memory'] == memory['memory']:
                        outf.write(section.getvalue())
                        outf.write('\n\n')
                    else:
                        nsections.append(section)
                sections = nsections
            # write any sections without a valid memory?
            if sections:
                outf.write('    /* misc sections */\n')
                for section in sections:
                    outf.write(section.getvalue())
                    outf.write('\n\n')
            outf.write('}\n')
            outf.write('\n')

@outputs.output('sys')
@outputs.output('box')
class LDScriptOutput_(ParialLDScriptOutput_):
    """
    Name of file to target for the linkerscript.
    """
    __argname__ = "ldscript_"
    __arghelp__ = __doc__

    def __init__(self, box, path=None,
            symbol_prefix='__',
            section_prefix='.',
            memory_prefix=''):
        super().__init__(box, path,
            symbol_prefix=symbol_prefix,
            section_prefix=section_prefix,
            memory_prefix=memory_prefix)

        for memory in box.memories:
            self.memories.append(memory)

        decl_i = 0
        # write out rom sections
        outf = self.sections.append(
            section='%(section_prefix)s' + 'text',
            memory='%(memory_prefix)s' + box.bestmemory('rx').name)
        outf.write('%(section)s : {\n')
        with outf.pushindent():
            outf.write('. = ALIGN(%(align)d);\n')
            outf.write('%(symbol_prefix)stext = .;\n')
            outf.write('*(%(section_prefix)stext*)\n')
            outf.write('*(%(section_prefix)srodata*)\n')
            outf.write('*(%(section_prefix)sglue_7*)\n')
            outf.write('*(%(section_prefix)sglue_7t*)\n')
            outf.write('*(%(section_prefix)seh_frame*)\n')
            outf.write('KEEP(*(%(section_prefix)sinit*))\n')
            outf.write('KEEP(*(%(section_prefix)sfini*))\n') # TODO oh boy there's a lot of other things
            outf.write('. = ALIGN(%(align)d);\n')
            outf.write('%(symbol_prefix)stext_end = .;\n')
            outf.write('%(symbol_prefix)sdata_init = .;\n')
        outf.write('} > %(MEMORY)s')

        # write out ram sections
        if box.stack:
            self.decls.insert(decl_i, '%(symbol)-16s = '
                'DEFINED(%(symbol)s) ? %(symbol)s : %(size)#010x;',
                symbol='%(symbol_prefix)s' + 'stack_min',
                size=box.stack.size)
            decl_i += 1
            outf = self.sections.append(
                section='%(section_prefix)s' + 'stack',
                memory='%(memory_prefix)s' + box.bestmemory('rw').name)
            outf.write('%(section)s (NOLOAD) : {\n')
            with outf.pushindent():
                outf.write('. = ALIGN(%(align)d);\n')
                outf.write('%(symbol_prefix)sstack = .;\n')
                outf.write('. += %(symbol_prefix)sstack_min;\n')
                outf.write('. = ALIGN(%(align)d);\n')
                outf.write('%(symbol_prefix)sstack_end = .;\n')
            outf.write('} > %(MEMORY)s')

        outf = self.sections.append(
            section='%(section_prefix)s' + 'data',
            memory='%(memory_prefix)s' + box.bestmemory('rw').name)
        outf.write('%(section)s : AT(%(symbol_prefix)sdata_init) {\n')
        with outf.pushindent():
            outf.write('. = ALIGN(%(align)d);\n')
            outf.write('%(symbol_prefix)sdata = .;\n')
            outf.write('*(%(section_prefix)sdata*)\n')
            outf.write('. = ALIGN(%(align)d);\n')
            outf.write('%(symbol_prefix)sdata_end = .;\n')
        outf.write('} > %(MEMORY)s')

        outf = self.sections.append(
            section='%(section_prefix)s' + 'bss',
            memory='%(memory_prefix)s' + box.bestmemory('rw').name)
        outf.write('%(section)s (NOLOAD) : {\n')
        with outf.pushindent():
            outf.write('. = ALIGN(%(align)d);\n')
            outf.write('%(symbol_prefix)sbss = .;\n')
            # TODO hm
            outf.write('%(symbol_prefix)sbss_start__ = .;\n')
            outf.write('*(%(section_prefix)sbss*)\n')
            if outf['section_prefix'] == '.':
                outf.write('*(COMMON)\n')
            outf.write('. = ALIGN(%(align)d);\n')
            outf.write('%(symbol_prefix)sbss_end = .;\n')
            outf.write('%(symbol_prefix)sbss_end__ = .;\n')
        outf.write('} > %(MEMORY)s')

        if box.heap:
            self.decls.insert(decl_i, '%(symbol)-16s = '
                'DEFINED(%(symbol)s) ? %(symbol)s : %(size)#010x;',
                symbol='%(symbol_prefix)s' + 'heap_min',
                size=box.heap.size)
            decl_i += 1
            outf = self.sections.append(
                section='%(section_prefix)s' + 'heap',
                memory='%(memory_prefix)s' + box.bestmemory('rw').name)
            outf.write('%(section)s (NOLOAD) : {\n')
            with outf.pushindent():
                outf.write('. = ALIGN(%(align)d);\n')
                if outf['section_prefix'] == '.':
                    outf.write('__end__ = .;\n')
                    outf.write('PROVIDE(end = .);\n')
                outf.write('%(symbol_prefix)sheap = .;\n')
                # TODO need all these?
                outf.write('%(symbol_prefix)sHeapBase = .;\n')
                outf.write('. += ORIGIN(%(MEMORY)s) + LENGTH(%(MEMORY)s);\n')
                outf.write('. = ALIGN(%(align)d);\n')
                outf.write('%(symbol_prefix)sheap_end = .;\n')
                # TODO need all these?
                outf.write('%(symbol_prefix)sHeapLimit = .;\n')
                outf.write('%(symbol_prefix)sheap_limit = .;\n')
            outf.write('} > %(MEMORY)s\n')
            outf.write('ASSERT(%(symbol_prefix)sheap_end - '
                '%(symbol_prefix)sheap > %(symbol_prefix)sheap_min,\n')
            outf.write('    "Not enough memory for heap")\n')

        # need interrupt vector?
        if box.issys():
            # TODO need this?
            # TODO configurable?
            self.decls.insert(0, 'ENTRY(Reset_Handler)')
            decl_i += 1
            self.decls.insert(decl_i, '%(symbol)-16s = '
                'DEFINED(%(symbol)s) ? %(symbol)s : %(size)#010x;',
                symbol='%(symbol_prefix)s' + 'isr_vector_min',
                size=0x400) # TODO configure this?
            decl_i += 1
            outf = self.sections.insert(0,
                section='%(section_prefix)s' + 'isr_vector',
                memory='%(memory_prefix)s' + box.bestmemory('r').name)
            outf.write('.isr_vector : {\n')
            with outf.pushindent():
                outf.write('. = ALIGN(%(align)d);\n')
                outf.write('%(symbol_prefix)sisr_vector = .;\n')
                outf.write('KEEP(*(%(section_prefix)sisr_vector))\n')
                outf.write('. = %(symbol_prefix)sisr_vector +'
                    '%(symbol_prefix)sisr_vector_min;\n')
                outf.write('. = ALIGN(%(align)d);\n')
                outf.write('%(symbol_prefix)sisr_vector_end = .;\n')
            outf.write('} > %(MEMORY)s')

@outputs.output('sys')
@outputs.output('box')
class LinkerScriptOutput(outputs.Output):
    """
    Name of file to target for the linkerscript.
    """
    __argname__ = "ldscript"
    __arghelp__ = __doc__

    def __init__(self, sys, box, path):
        self._decls = []
        self._memories = []
        self._sections = []
        super().__init__(sys, box, path)

    def append_decl(self, fmt=None, **kwargs):
        outf = self.mkfield(**kwargs)
        self._decls.append(outf)
        if fmt is not None:
            outf.write(fmt)
        return outf

    def append_memory(self, fmt=None, **kwargs):
        outf = self.mkfield(**kwargs)
        self._memories.append(outf)
        if fmt is not None:
            outf.write(fmt)
        return outf

    def append_section(self, fmt=None, **kwargs):
        outf = self.mkfield(**kwargs)
        self._sections.append(outf)
        if fmt is not None:
            outf.write(fmt)
        return outf

    def build(self, outf):
        outf.write('/***** AUTOGENERATED *****/\n')
        outf.write('\n')
        if self._decls:
            for decl in self._decls:
                outf.write(decl.getvalue())
                outf.write('\n')
            outf.write('\n')
        if self._memories:
            outf.write('MEMORY {\n')
            for memory in self._memories:
                for line in memory.getvalue().strip().split('\n'):
                    outf.write(4*' ' + line + '\n')
            outf.write('}\n')
            outf.write('\n')
        if self._sections:
            outf.write('SECTIONS {\n')
            for i, section in enumerate(self._sections):
                for line in section.getvalue().strip().split('\n'):
                    outf.write(4*' ' + line + '\n')
                if i < len(self._sections)-1:
                    outf.write('\n')
            outf.write('}\n')
            outf.write('\n')

@outputs.output('sys')
@outputs.output('box')
class PartialLinkerScriptOutput(LinkerScriptOutput):
    """
    Name of file to target for a partial linkerscript. This is the minimal
    additions needed for a bento box and should be imported into a traditional
    linkerscript to handle the normal program sections.
    """
    __argname__ = "partial_ldscript"
    __arghelp__ = __doc__
