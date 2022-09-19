def to_rgb(hex):
    return tuple([int(hex[i:i+2],16) for i in range(0,6,2)])

def mix(im,color):
    r,g,b = color
    im[:,:,0] = im[:,:,0]*(r/255)
    im[:,:,1] = im[:,:,1]*(g/255)
    im[:,:,2] = im[:,:,2]*(b/255)
    return im