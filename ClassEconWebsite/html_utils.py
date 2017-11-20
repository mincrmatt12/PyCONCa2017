import re

##
## -- this was stolen from djanjo. all credit to them.
##

re_words = re.compile(r'&.*?;|<.*?>|(\w[\w-]*)', re.U|re.S)
re_chars = re.compile(r'<.*?>|(.)', re.U | re.S)
re_tag = re.compile(r'<(/)?([^ ]+?)(?:(\s*/)| .*?)?>', re.S)
re_newlines = re.compile(r'\r\n|\r')  # Used in normalize_newlines
re_camel_case = re.compile(r'(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))')
def add_truncation_text(text, truncate='...'):
    if truncate == None:
        truncate == '...'
    if '%(truncated_text)s' in truncate:
        return truncate % {'truncated_text': text}
    # The truncation text didn't contain the %(truncated_text)s string
    # replacement argument so just append it to the text.
    if text.endswith(truncate):
        # But don't append the truncation text if the current text already
        # ends in this.
        return text
    return '%s%s' % (text, truncate)
def split(num, inp, truncate='<p class="small text-center" data-container="body" data-toggle="tooltip" title="Click \'Goto post page\' to read the rest of this post"><span class="glyphicon glyphicon-option-horizontal"></span></p>'):
    """
    Truncates a string after a certain number of words. Takes an optional
    argument of what should be used to notify that the string has been
    truncated, defaulting to ellipsis (...).
    """
    length = int(num)
    return truncate_html(length, truncate, inp, length, True)
    


def truncate_html(length, truncate, text, truncate_len, words):
    """
    Truncates HTML to a certain number of chars (not counting tags and
    comments), or, if words is True, then to a certain number of words.
    Closes opened tags if they were correctly closed in the given HTML.

    Newlines in the HTML are preserved.
    """
    if words and length <= 0:
        return ''

    html4_singlets = (
        'br', 'col', 'link', 'base', 'img',
        'param', 'area', 'hr', 'input'
    )

    # Count non-HTML chars/words and keep note of open tags
    pos = 0
    end_text_pos = 0
    current_len = 0
    open_tags = []

    regex = re_words if words else re_chars

    while current_len <= length:
        m = regex.search(text, pos)
        if not m:
            # Checked through whole string
            break
        pos = m.end(0)
        if m.group(1):
            # It's an actual non-HTML word or char
            current_len += 1
            if current_len == truncate_len:
                end_text_pos = pos
            continue
        # Check for tag
        tag = re_tag.match(m.group(0))
        if not tag or current_len >= truncate_len:
            # Don't worry about non tags or tags after our truncate point
            continue
        closing_tag, tagname, self_closing = tag.groups()
        # Element names are always case-insensitive
        tagname = tagname.lower()
        if self_closing or tagname in html4_singlets:
            pass
        elif closing_tag:
            # Check for match in open tags list
            try:
                i = open_tags.index(tagname)
            except ValueError:
                pass
            else:
                # SGML: An end tag closes, back to the matching start tag,
                # all unclosed intervening start tags with omitted end tags
                open_tags = open_tags[i + 1:]
        else:
            # Add it to the start of the open tags list
            open_tags.insert(0, tagname)

    if current_len <= length:
        return text
    out = text[:end_text_pos]
    truncate_text = add_truncation_text('', truncate)
    if truncate_text:
        out += truncate_text
    # Close any tags still open
    for tag in open_tags:
        out += '</%s>' % tag
    # Return string
    return out
