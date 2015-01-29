# -*- coding: utf-8 -*-
import lxml.html
import types


def xhtmlContentIsEmpty(xhtmlContent):
    '''This method checks if given p_xhtmlContent will produce someting on rendering.
       p_xhtmlContent can either be a string or already a lxml.html element.'''
    # first check if xhtmlContent is not simply None or so
    isStr = isinstance(xhtmlContent, types.StringType) or isinstance(xhtmlContent, types.NoneType)
    if isStr and (not xhtmlContent or not xhtmlContent.strip()):
        return True

    if isStr:
        xhtmlContent = "<special_tag>%s</special_tag>" % xhtmlContent
        tree = lxml.html.fromstring(unicode(xhtmlContent, 'utf-8'))
    else:
        tree = xhtmlContent
    if tree.tag == 'special_tag':
        if tree.getchildren():
            for el in tree.getchildren():
                if bool(el.text_content().strip()) or bool(el.attrib) or bool(el.getchildren()):
                    return False
            return True

    # if xhtmlContent renders text or has attributes or has children, we consider it not empty
    return not bool(tree.text_content().strip()) and not bool(tree.attrib) and not bool(tree.getchildren())


def removeBlanks(xhtmlContent):
    '''This method will remove any blank line in p_xhtmlContent.'''
    if not xhtmlContent or not xhtmlContent.strip():
        return xhtmlContent
    # surround xhtmlContent with a special tag so we are sure that tree is always
    # a list of children of this special tag
    xhtmlContent = "<special_tag>%s</special_tag>" % xhtmlContent
    tree = lxml.html.fromstring(unicode(xhtmlContent, 'utf-8'))
    for el in tree.getchildren():
        # el can be a subtree, like <ul><li>...</li></ul> we must consider entire rendering of it
        if xhtmlContentIsEmpty(el):
            el.getparent().remove(el)
    # only return children of the <special_tag>
    return ''.join([lxml.html.tostring(x, encoding='utf-8', pretty_print=True, method='xml') for x in tree.iterchildren()])


def addClassToLastChildren(xhtmlContent,
                           classNames={'p': 'pmParaKeepWithNext',
                                       'li': 'podItemKeepWithNext'},
                           tags=('p', 'ul', 'li', ),
                           numberOfChars=60):
    '''This method will add a class attribute adding class correspondig to tag given in p_classNames
       to the last tags of given p_xhtmlContent.
       It only consider given p_tags and will define the class on last tags until it contains given
       p_numberOfChars number of characters.
    '''
    if not xhtmlContent or not xhtmlContent.strip():
        return xhtmlContent

    # surround xhtmlContent with a special tag so we are sure that tree is always
    # a list of children of this special tag
    tree = lxml.html.fromstring(unicode("<special_tag>%s</special_tag>" % xhtmlContent.strip(), 'utf-8'))
    children = tree.getchildren()
    if not children:
        return xhtmlContent

    def adaptTree(children, managedNumberOfChars=0):
        """
          Recursive method that walk the children and subchildren and adapt what necessary.
        """
        # apply style on last element until we reached necessary numberOfChars or we encounter
        # a tag not in p_tags or we do not have a tag...
        i = 1
        stillNeedToAdaptPreviousChild = True
        numberOfChildren = len(children)
        while stillNeedToAdaptPreviousChild and i <= numberOfChildren:
            child = children[-i]
            if not child.tag in tags:
                stillNeedToAdaptPreviousChild = False
            else:
                subchildren = child.getchildren()
                if subchildren:
                    # recursion is done here
                    managedNumberOfChars = adaptTree(subchildren, managedNumberOfChars=managedNumberOfChars)
                else:
                    # check if tag did not already have a class attribute
                    # in this case, we append classNames[child.tag] to existing classes
                    if 'class' in child.attrib:
                        child.attrib['class'] = '{0} {1}'.format(classNames[child.tag], child.attrib['class'])
                    else:
                        child.attrib['class'] = classNames[child.tag]
                    managedNumberOfChars += child.text and len(child.text) or 0
                if managedNumberOfChars >= numberOfChars:
                    stillNeedToAdaptPreviousChild = False
                i = i + 1
        return managedNumberOfChars

    # call recursive method 'adaptTree' that whill adapt children and subchildren
    adaptTree(children)

    return ''.join([lxml.html.tostring(x, encoding='utf-8', pretty_print=True, method='xml') for x in tree.iterchildren()])
