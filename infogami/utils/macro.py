"""
Macro extension to markdown.

Macros take argument string as input and returns result as markdown text.
"""
import markdown
import web

_macros = {}

def macro(f):
    """Decorator to register a markdown macro.
    Macro is a function that takes argument string and returns result as markdown string.
    """
    register_macro(f.__name__, f)
    return f
    
def register_macro(name, f):
    _macros[name] = f

def eval_template(t, args):
    return result.args
    
def call_macro(name, args):
    if name in _macros:
        try:
            f = _macros[name]
            #@@ crude way of calling macro after evaluating args.
            x = web.template.Template("$def with (f)\n$var result: $f(%s)" % args)(f)
            result = x.result
        except Exception, e:
            result = "%s failed with error: <pre>%s</pre>" % (name, web.websafe(str(e)))
            
        return result
    else:
        return "Unknown macro: <pre>%s</pre>" % name

class MacroPattern(markdown.BasePattern):
    """Inline pattern to replace macros."""
    def __init__(self, stash):
        pattern = r'{{(.*)\((.*)\)}}'
        markdown.BasePattern.__init__(self, pattern)
        self.stash = stash

    def handleMatch(self, m, doc):
        name, args = m.group(2), m.group(3)
        html = call_macro(name, args)

        # markdown uses place-holders to replace html blocks. 
        # markdown.HtmlStash stores the html blocks to be replaced
        placeholder = self.stash.store(html)
        return doc.createTextNode(placeholder)

def macromarkdown(md):
    """Adds macro extenstions to the specified markdown instance."""
    md.inlinePatterns.append(MacroPattern(md.htmlStash))
    return md

@macro
def HelloWorld():
    """Hello world macro."""
    return "<b>Hello, world</b>."

@macro
def ListOfMacros():
    """Lists all available macros."""
    out = ""
    out += "<ul>"
    for k in sorted(_macros.keys()):
        out += '  <li><b>%s</b>: %s</li>\n' % (k, _macros[k].__doc__ or "")
    out += "</ul>"
    return out
    
if __name__ == "__main__":
    def get_markdown(text):
        md = markdown.Markdown(source=text, safe_mode=False)
        md = macromarkdown(md)
        return md
    
    print get_markdown("This is HelloWorld Macro. {{HelloWorld()}}\n\n" + 
            "And this is the list of available macros. {{ListOfMacros()}}")
