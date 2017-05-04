import numpy as np
import cv2
import math
import matplotlib.pyplot as plt

##### Input #####
# Camera properties
ang = 12.5 # deg
fps = 1;
AR = 3/2;

# Target properties
dia = 0.1 # m

# Initial nozzle position guess
y_guess = 0.5 # fraction
z_guess = 0.5 # fraction
d_guess = 30.48  # m

##### Begin algorithm #####
# Open video file
cap     = cv2.VideoCapture('70mm_LR.mov')
width   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
length  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Open output video
fourcc  = cv2.VideoWriter_fourcc(*'XVID')
out     = cv2.VideoWriter('output.avi',fourcc, 20.0, (width,height))
out2    = cv2.VideoWriter('processed.avi',fourcc, 20.0, (width,height))

# Initialize arrays
frames  = np.zeros(length)      # time,                 s
y       = np.zeros(length)      # horizontal distance,  m
yp      = np.zeros(length)      # horizontal distance,  pixels
z       = np.zeros(length)      # vertical distance,    m
zp      = np.zeros(length)      # vertical distance,    pixels
d       = np.zeros(length)      # range,                m
w       = np.zeros(length)      # horizon width,        m
diap    = np.zeros(length)      # diameter of nozzle,   pixels

frames[0] = 1;

# Horizon guess
w[0] = 2*d_guess*math.tan(ang*math.pi/180)

# Position guess
yp[0]   = y_guess*width
zp[0]   = z_guess*height
y[0]    = -(y_guess-0.5)*w[0]
z[0]    = (z_guess-0.5)*w[0]

# Range guess
d[0]    = d_guess
diap[0] = dia*(width/w[0])/AR 

for ii in range(0,length-1):
    # Get single frame
    ret, frame = cap.read()
    
    # Original image
    img = frame
    
    # Grayscale
    gimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Crop
    if ii < length/4:
        c = 0.1
        blur = 5
        p1 = 75
        p2  = 50
    elif ii < length/2:
        c = 0.1
        blur = 5
        p1 = 75
        p2 = 50
    elif ii < 3*length/4:
        c = 0.2
        blur = 5
        p1 = 100
        p2 = 55
    elif ii <= length:
        c = 0.3
        blur = 1
        p1 = 250
        p2 = 75
        
    cu = (0.5+c/2)
    cl = (0.5-c/2)
    
    yc1     = int(cl*width)+50
    yc2     = int(cu*width)+50
    zc1     = int(cl*height)+50
    zc2     = int(cu*height)+50
    cimg    = gimg[zc1:zc2,yc1:yc2]
    
    # Re-scale 
    scale = (width,height)
    simg    = cv2.resize(cimg, scale, interpolation = cv2.INTER_AREA)

    # Blur
    bimg = cv2.medianBlur(simg,blur)
    # bimg = cv2.Canny(simg,100,500)
    
    # Show processed image
    smallimg = cv2.resize(cimg, (960,540), interpolation = cv2.INTER_AREA)
    cv2.imshow('frame',smallimg)
    cv2.waitKey(50) 
    
    # Run HoughCircles
    try:
        circles = cv2.HoughCircles(bimg,cv2.HOUGH_GRADIENT,1,1,param1=p1,param2=p2,
                                   minRadius=0,maxRadius=0)
        circles = np.uint16(np.around(circles))
        
        # Draw found circle
        maxrc = 0
        for jj in circles[0,:]:
            # Draw the outer circle
            yc = int(jj[0]*c + cl*width + 50)
            zc = int(jj[1]*c + cl*height + 50)
            rc = int(jj[2]*c)
            cv2.circle(img,(yc,zc),rc,(1000,100,100),2)
            
            # Draw the center of the circle
            cv2.circle(img,(yc,zc),2,(1000,100,100),2)
            
            # Check for largest circle
            if maxrc < rc:
                maxyc = yc
                maxzc = zc
                maxrc = rc
        
        # Use largest circle
        yp[ii+1]    = maxyc
        zp[ii+1]    = maxzc
        diap[ii+1]  = 2*maxrc

    except:
        yp[ii+1]    = yp[ii]
        zp[ii+1]    = zp[ii]
        diap[ii+1]  = diap[ii]
    
    # Save frame
    out.write(img)
    
    # Save processed image
    pimg = cv2.cvtColor(bimg, cv2.COLOR_GRAY2BGR)
    out2.write(pimg)

    # Calculate horizon
    w[ii+1] = (dia/diap[ii+1])*width

    # Calculate new range
    d[ii+1] = w[ii+1] /(2*math.tan(ang*math.pi/180))
    # if (d[ii+1] > 2*d[ii]) or (d[ii+1] < 0.5*d[ii]):
    #    d[ii+1] = d[ii]
   
    # Calculate new position
    y[ii+1] = (-(yp[ii+1]-width/2)/width)*w[ii+1]
    z[ii+1] = ((zp[ii+1]-height/2)/height)*w[ii+1]/AR
    
    # Time
    frames[ii+1] = frames[ii] + 1


cv2.destroyAllWindows() 
    
# Close videos
cap.release()
out.release()
out2.release()
cv2.destroyAllWindows()

# On-screen position
plt.figure(figsize=(7, 7))
plt.plot(y,z)
plt.grid(True)
plt.xlabel('y')
plt.ylabel('z')
plt.savefig('yz.png')
plt.show()

# Position over time
plt.figure(figsize=(7, 7))
plt.plot(frames,y)
plt.plot(frames,z)
plt.grid(True)
plt.xlabel('Frames')
plt.ylabel('Meters')
plt.savefig('tyz.png')
plt.show()

# Range over time
plt.figure(figsize=(7, 7))
plt.plot(frames,d)
plt.grid(True)
plt.xlabel('Frames')
plt.ylabel('Range')
plt.savefig('Range.png')
plt.show()
