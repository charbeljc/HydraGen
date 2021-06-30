import logging
import dom
import binder
import walk
import logging

dom.logger.setLevel(logging.INFO)
binder.FLAGS.append("-I/usr/lib/llvm-12/include")

ctx = dom.Context(walk.FACTORY)
tu, index = binder.parse("llvm_bind.h", binder.FLAGS)

tx = dom.NodeProxy.make(tu.cursor, ctx)
tx.walk(ctx)
