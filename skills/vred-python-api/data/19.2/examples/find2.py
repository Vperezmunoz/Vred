# Find nodes with caching
# source: find2.html

# © 2026 Autodesk, Inc. All rights reserved.

# if you have many nodes and call findNode quite often you
# can use initFindCache() to speed it up. On a scene with
# 10000 nodes it is about 700 times faster!
newScene()

import time

print("Executing find2 script!")

# number of nodes to create and search
n = 5000

print("Started creating nodes")
name = "name"
for i in range(n):
    group = createNode("Group", name + str(i))
    
print("\nFinding nodes without cache\n")
# now find via a list of names
names = []
for i in range(n):
    names.append(name + str(i))

t = time.time()
for i in range(n):
    node = findNode(name + str(i))
print("Time needed for finding node separately: ", time.time() - t)

t = time.time()
nodes = findNodes(names)
print("Time needed for finding node list: ", time.time() - t)

print("\nNow using the cache:\n")

t = time.time()
# cache all nodes, gives a great speed improvement!
initFindCache()
print("Time needed to create cache: ", time.time() - t)

t = time.time()
for i in range(n):
    node = findNode(name + str(i))
print("Time needed for finding node separately: ", time.time() - t)

t = time.time()
nodes = findNodes(names)
print("Time needed for finding node list: ", time.time() - t)
clearFindCache()
