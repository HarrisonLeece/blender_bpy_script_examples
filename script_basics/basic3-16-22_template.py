import bpy
import numpy as np

def render_image_indexed(output_dir, out_type, step, ani_length):
    string_order= int(np.ceil(np.log10(ani_length+1)))
    index_order = int(np.ceil(np.log10(step+1)))
    out_string = ""
    
    for i in range(string_order-index_order):
        out_string += "0"
    if (step != 0):
        out_string += str(int(step))
    bpy.context.scene.render.filepath = output_dir+out_string
    bpy.ops.render.render(write_still = True)


def map_to_exponent_large2small(input_vector, start, end):
    output = []
    p = np.linspace(0,1.011,len(input_vector))
    #max_value = -100*np.e**(3.39*0-8) + 1.034
    max_value = start
    #-1*(100*np.e**(3.39x - 8))+1
    for i in range(len(input_vector)):
        k = max_value
        out = round((k*((-100*np.e**(3.39*p[i] - 8))+1.034)),8) + end
        print(out)
        output.append(out)
    return output

def clear_all_data():
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.select_set(True)
        else:
            obj.select_set(False)
        bpy.ops.object.delete()
    
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)

    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)

def create_plane(number, position):
    return false

#https://vividfax.github.io/2021/01/14/blender-materials.html
def newMaterial(id):

    mat = bpy.data.materials.get(id)

    if mat is None:
        mat = bpy.data.materials.new(name=id)

    mat.use_nodes = True

    if mat.node_tree:
        mat.node_tree.links.clear()
        mat.node_tree.nodes.clear()

    return mat

def newShader(id, type, r, g, b, a):

    mat = newMaterial(id)

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    output = nodes.new(type='ShaderNodeOutputMaterial')

    if type == "diffuse":
        shader = nodes.new(type='ShaderNodeBsdfDiffuse')
        nodes["Diffuse BSDF"].inputs[0].default_value = (r, g, b, a)

    elif type == "emission":
        shader = nodes.new(type='ShaderNodeEmission')
        nodes["Emission"].inputs[0].default_value = (r, g, b, a)
        nodes["Emission"].inputs[1].default_value = 1

    elif type == "glossy":
        shader = nodes.new(type='ShaderNodeBsdfGlossy')
        nodes["Glossy BSDF"].inputs[0].default_value = (r, g, b, a)
        nodes["Glossy BSDF"].inputs[1].default_value = 0

    links.new(shader.outputs[0], output.inputs[0])

    return mat
        
    
