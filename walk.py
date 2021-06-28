from clang.cindex import (Cursor, CursorKind, TranslationUnit,
                          TranslationUnitLoadError)
from logzero import logger

from dom import (FACTORY, Class, ClassTemplate,
                 ClassTemplatePartialSpecialization, Enum, Function,
                 FunctionTemplate, Method, Namespace, Struct, TxUnit)

def is_scope(node):
    return node and node.kind in (
        CursorKind.CLASS_DECL,
        CursorKind.CLASS_TEMPLATE,
        CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION,
        CursorKind.CONSTRUCTOR,
        CursorKind.CXX_METHOD,
        CursorKind.ENUM_DECL,
        CursorKind.FUNCTION_DECL,
        CursorKind.FUNCTION_TEMPLATE,
        CursorKind.NAMESPACE,
        CursorKind.CONSTRUCTOR,
        CursorKind.STRUCT_DECL,
        CursorKind.ENUM_DECL,
        CursorKind.TRANSLATION_UNIT,
    )


def is_functional(node):
    return node and node.kind in (
        CursorKind.FUNCTION_DECL,
        CursorKind.FUNCTION_TEMPLATE,
        CursorKind.CXX_METHOD,
        CursorKind.CONSTRUCTOR
    )

def is_pop(node):
    return node and node.kind == CursorKind.UNEXPOSED_DECL

def walk(tu: TranslationUnit):
    stack = []
    elements = {}
    objs = []
    current = None
    for node in tu.cursor.walk_preorder():
        usr = node.get_usr()
        obj = None
        if usr:
            obj = elements.get(usr)

        if not obj and FACTORY.get(node.kind):
            obj = FACTORY[node.kind](node.spelling, node)
            objs.append(obj)
            # logger.warning("%s", obj)
            if obj.usr:
                elements[obj.usr] = obj
            
        if obj:
            if is_scope(obj.node):
                if current:
                    logger.debug("PUSH: %s", obj)
                    stack.append(current)
                current = obj
            else:
                logger.debug("check: %s", obj)
                sparent = obj.node.semantic_parent
                if not sparent or not sparent.get_usr():
                    logger.debug("node: %s, no sparent or anonymous", node)
                    pass
                
                else:
                    sparent_usr = sparent.get_usr()
                    logger.debug("node: %s SPARENT %s,  CURRENT: %s", obj, sparent_usr, current.usr)
                    while sparent_usr != current.usr:
                        logger.debug("POP: %s", current)
                        current = stack.pop()
                    current.accept(obj)
        else:
            #logger.debug("skipped %s", node.kind)
            pass

    return stack, elements, objs



def walk2(tu: TranslationUnit):

    stack = []
    current = None
    for node in tu.cursor.walk_preorder():
        if is_scope(node):
            if not current:
                current = node
                assert not stack
        
        usr = node.get_usr()
        sparent_usr = node.semantic_parent.get_usr() if node.semantic_parent else None
        lparent_usr = node.lexical_parent.get_usr() if node.lexical_parent else None
        if (sparent_usr != lparent_usr):
            logger.debug("kind:%s spelling:%r usr: %r, sparent_usr: %r, lparent_usr: %r", node.kind, node.spelling, usr, sparent_usr, lparent_usr)


def kind(node):
    return (node.kind, node.spelling) if node else None

def walk3(tu: TranslationUnit):
    stack = []
    current = None

    for node in tu.cursor.walk_preorder():
        deep = len(stack) * " "
        logger.debug("%snode: %s current: %s, stack: %s", deep, kind(node), kind(current), list(map(kind, stack)))
        if is_functional(node):
            if is_functional(current):
                logger.debug("%sswap(1) %s and %s", deep, kind(node), kind(current))
                if current.semantic_parent == node.semantic_parent:
                    logger.debug("ok, same parent")
                else:
                    logger.debug("not same parents!, pop")
                    current = stack.pop()
                    if current.semantic_parent == node.semantic_parent:
                        logger.debug("ok, same parent")
                    else:
                        logger.debug("giving up!!!")
                current = node
            else:
                if current:
                    logger.debug("%spush %s", deep, kind(current))
                    stack.append(current)
                current = node
        elif is_scope(node):
            if current and not is_functional(current):
                logger.debug("%spush %s", deep, kind(current))
                stack.append(current)
            else:
                logger.debug("%sswap(2) %s and %s", deep, kind(node), kind(current))
            current = node
        elif is_pop(node):
            current = stack.pop()
            logger.debug("%spop %s", deep, kind(current))
        else:
            logger.debug("%saccept %s in %s", deep, kind(node), kind(current))
    return stack, current