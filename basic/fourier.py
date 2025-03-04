
class FourierTuple(object):
    """
    FourierTuple: Stores ft plan, real volume and complex volume
    """
    def __init__(self,plan,real,complexVolume):
        self.plan = plan
        self.real = real
        self.complexVolume = complexVolume

class FtSingleton(object):
    """
    FtSingleton: manages plans for different volume sizes. If it lacks a plan, a new one will be generated. In addition, a real and complex volume.
    Values are copied to these volumes for each transformation.  
    Aim - no plan will be generated twice.
    G{classtree}
    """   
    ftList = []
    iftList = []      
       
    def addFt(self,theTuple):
        """
        addFt: appends a Fourier Tuple to ftList
        @param theTuple: Fourier Tuple
        @author: Thomas Hrabe 
        """
        self.ftList.append(theTuple)
    
    def addiFt(self,theTuple):
        """
        addiFt: appends a Fourier Tuple to iftList
        @param theTuple: Fourier Tuple
        @author: Thomas Hrabe 
        """
        self.iftList.append(theTuple)

    def findInFt(self,volume):
        """
        findInFt: Checks for Fourier Tuple with same volume size. 
        @param volume:
        @type volume: L{pytom_volume.vol} 
        @return: 
        @author: Thomas Hrabe 
        """
        length = len(self.ftList)
        found = False
        it = 0
        x = volume.sizeX()
        y = volume.sizeY()
        z = volume.sizeZ()
        
        t = None
        while (not found) and (it < length):
            theTuple = self.ftList[it]
            
            if x == theTuple.real.sizeX() and y == theTuple.real.sizeY() and z == theTuple.real.sizeZ():
                found = True
                t = theTuple
            else:
                it += 1
        
        return t
        
    def findIniFt(self,volume):
        """
        findIniFt: Checks for Fourier Tuple with same volume size.
        @param volume:
        @return: 
        @author: Thomas Hrabe 
        """

        length = len(self.iftList)
        found = False
        it = 0
        
        x = volume.getFtSizeX()
        y = volume.getFtSizeY()
        z = volume.getFtSizeZ()
        
        if x == 0 and y == 0 and z == 0:
            x = volume.sizeX() / 2
            y = volume.sizeY() / 2
            z = (volume.sizeZ() + 1)* 2
            
        t = None
        while (not found) and (it < length):
            theTuple = self.iftList[it]
            
            if x == theTuple.real.sizeX() and y == theTuple.real.sizeY() and z == theTuple.real.sizeZ():
                found = True
                t = theTuple
            else:
                it += 1
        
        return t

def fft(data, scaling=''):
    """
    fft: Performs Fourier Transformation on input. The result is NOT scaled in any way (1/N , 1/sqrt(n),...)  
    @param data: The source volume.  
    @type data: pytom_volume.vol
    @param scaling: Describes the type of scaling is applied. 'N' 1/N, 'sqrtN' 1/sqrt(N). '' no scaling (default)
    @type scaling: str
    @rtype: pytom_volume.vol_comp
    @return: The fourier transformed data 
    @author: Thomas Hrabe
    """
    import pytom_volume
    
    if not data.__class__ == pytom_volume.vol:
        raise TypeError('Data must be of type pytom_volume.vol')
    
    
    ftSingleton = FtSingleton()
    
    theTuple = ftSingleton.findInFt(data)
    
    if not theTuple == None:
        plan = theTuple.plan
        
        theTuple.real.copyVolume(data)
        plan.transform()
        
        returnValue = pytom_volume.vol_comp(theTuple.complexVolume.sizeX(),theTuple.complexVolume.sizeY(),theTuple.complexVolume.sizeZ())
        returnValue.copyVolume(theTuple.complexVolume)
        
        returnValue.setFtSizeX(data.sizeX())
        returnValue.setFtSizeY(data.sizeY())
        returnValue.setFtSizeZ(data.sizeZ())


        if scaling=='sqrtN':
            from numpy import sqrt
            returnValue = returnValue / sqrt(data.sizeX()*data.sizeY()*data.sizeZ())
        if scaling == 'N':
            from numpy import sqrt
            returnValue = returnValue / (data.sizeX() * data.sizeY() * data.sizeZ())

        return returnValue
    
    else:  
        import pytom_fftplan
    
        real = pytom_volume.vol(data.sizeX(),data.sizeY(),data.sizeZ())
        real.copyVolume(data)
        
        if(data.sizeZ() > 1):
            complexVolume = pytom_volume.vol_comp(data.sizeX(),data.sizeY(),data.sizeZ()//2+1)
            returnValue = pytom_volume.vol_comp(data.sizeX(),data.sizeY(),data.sizeZ()//2+1)
        else:
            complexVolume = pytom_volume.vol_comp(data.sizeX(),data.sizeY()//2+1,1)
            returnValue = pytom_volume.vol_comp(data.sizeX(),data.sizeY()//2+1,1)
            
        plan = pytom_fftplan.plan(real,complexVolume)
        plan.transform()
        returnValue.copyVolume(complexVolume)
    
        returnValue.setFtSizeX(data.sizeX())
        returnValue.setFtSizeY(data.sizeY())
        returnValue.setFtSizeZ(data.sizeZ())
    
        theTuple = FourierTuple(plan,real,complexVolume)
        
        ftSingleton.addFt(theTuple)

        if scaling=='sqrtN':
            from numpy import sqrt
            returnValue = returnValue / sqrt(data.sizeX()*data.sizeY()*data.sizeZ())
        elif scaling == 'N':
            from numpy import sqrt
            returnValue = returnValue / (data.sizeX() * data.sizeY() * data.sizeZ())

        return returnValue

def ifft(Fdata, scaling=''):

    """
    ifft: Performs inverse Fourier Transformation on input. The result is NOT scaled in any way (1/N , 1/sqrt(n),...)
    @param Fdata: The source volume (must be complex). If FData does not have shape information of the real volume, PyTom will assume that x==y==z (See line 198)   
    @type Fdata: pytom_volume.vol_comp
    @param scaling: Describes the type of scaling is applied. 'N' 1/N, 'sqrtN' 1/sqrt(N). '' no scaling (default)
    @type scaling: str
    @rtype: pytom_volume.vol
    @return: The inverse fourier transformed data
    @author: Thomas Hrabe
    """
    import pytom_volume
    
    if not Fdata.__class__ == pytom_volume.vol_comp:
        raise TypeError('Data must be of type pytom_volume.vol_comp')
    
    if scaling: Fdata = Fdata/Fdata.getFtSizeX()/Fdata.getFtSizeY()/Fdata.getFtSizeZ()

    ftSingleton = FtSingleton()
    
    theTuple = ftSingleton.findIniFt(Fdata)
    
    if not theTuple == None:
        plan = theTuple.plan
        
        theTuple.complexVolume.copyVolume(Fdata)
        plan.transform()
        
        returnValue = pytom_volume.vol(theTuple.real.sizeX(),theTuple.real.sizeY(),theTuple.real.sizeZ())
        returnValue.copyVolume(theTuple.real)
        if scaling=='sqrtN':
            from numpy import sqrt
            returnValue = returnValue / sqrt(Fdata.sizeX()*Fdata.sizeY()*Fdata.sizeZ())
        if scaling == 'N':
            from numpy import sqrt
            returnValue = returnValue / (Fdata.sizeX() * Fdata.sizeY() * Fdata.sizeZ())

        return returnValue
    
    else:  
        import pytom_fftplan
    
        complexVolume = pytom_volume.vol_comp(Fdata.sizeX(),Fdata.sizeY(),Fdata.sizeZ())
        complexVolume.copyVolume(Fdata)
        
        x = Fdata.getFtSizeX()
        y = Fdata.getFtSizeY()
        z = Fdata.getFtSizeZ()
        
        if x == 0 and y == 0 and z == 0:
            x = Fdata.sizeX() 
            y = Fdata.sizeY() 
            z = (Fdata.sizeZ() - 1)* 2
            
            if x == y and abs(z-y) == 1:
                #if x == y and x is odd, then z will be one pixel off. 
                #adjust accordingly that x == y == z
                z = y 
                print('Warning: PyTom assumes that the shape of the real volume is :',x,y,z)
                print('Warning: Check if that is consistent with your data!')
                
        real = pytom_volume.vol(int(x),int(y),int(z))
        returnValue = pytom_volume.vol(int(x),int(y),int(z))
        
        plan = pytom_fftplan.plan(complexVolume,real)    
        plan.transform()
        returnValue.copyVolume(real)
    
        theTuple = FourierTuple(plan,real,complexVolume)
        
        ftSingleton.addiFt(theTuple)
        if scaling=='sqrtN':
            from numpy import sqrt
            returnValue = returnValue / sqrt(Fdata.sizeX()*Fdata.sizeY()*Fdata.sizeZ())
        if scaling == 'N':
            from numpy import sqrt
            returnValue = returnValue / (Fdata.sizeX() * Fdata.sizeY() * Fdata.sizeZ())

        return returnValue
    
def ftshift(data, inplace = True):
    """
    ftshift: Performs a forward fourier shift of data. Data must be full, the center is not determined accordingly. Assumes center is always size/2.
    @param data: - a volume
    @type data: pytom_volume.vol or pytom_volume.vol_comp
    @param inplace: true by default
    @type inplace: boolean
    @return: data shifted
    @author: Thomas Hrabe
    """
    import pytom_fftplan
    if inplace:
        pytom_fftplan.fftShift(data,False)
        return None
    else:
        from pytom_volume import vol, vol_comp
        if data.__class__ == vol:
            dummy = vol(data)
        elif data.__class__ == vol_comp:
            dummy = vol_comp(data)
        pytom_fftplan.fftShift(dummy,False)
        return dummy

def iftshift(data, inplace = True):
    """
    iftshift: Performs a inverse fourier shift of data. Data must be full, the center is not determined accordingly. Assumes center is always size/2.
    @param data: - a volume
    @type data: pytom_volume.vol or pytom_volume.vol_comp 
    @return: data inverse shifted
    @author: Thomas Hrabe
    """
    import pytom_fftplan
    if inplace:
        pytom_fftplan.fftShift(data,True)
        return data
    else:
        from pytom_volume import vol, vol_comp
        if data.__class__ == vol:
            dummy = vol(data)
        elif data.__class__ == vol_comp:
            dummy = vol_comp(data)
        pytom_fftplan.fftShift(dummy,True)
        return dummy

def convolute(v, k, kernel_in_fourier=False):
    """
    @param v: the volume to be convolute
    @type v: L{pytom_volume.vol}
    @param k: the convolution kernel in real space
    @type k: L{pytom_volume.vol}
    @param kernel_in_fourier: the given kernel is already in Fourier space or not (full size, shifted in the center! \
        or reduced size). Default is False.
    @type kernel_in_fourier: L{bool}
    @return: Volume convoluted with kernel
    @rtype: L{pytom_volume.vol}
    """
    fv = fft(v)
    if not kernel_in_fourier:
        fk = fft(k)
        res = fv*fk
    else:
        from pytom_volume import complexRealMult, fullToReduced
        if k.sizeZ() == k.sizeX():
            fk = fullToReduced(ftshift(k, inplace=False))
        else:
            fk = k
        res = complexRealMult(fv, fk)
        
    out = ifft(res)
    out.shiftscale(0.0,1/float(out.sizeX()*out.sizeY()*out.sizeZ()))
    
    return out

def fourierSizeOperation(sizeX=0,sizeY=0,sizeZ=0,reducedToFull = True):
    """
    fourierSizeOperation: determines the fourier size given the three real-space size parameters and real-space size given three fourier-size parameters
    @param sizeX: 
    @param sizeY: 
    @param sizeZ:
    @param reducedToFull: 
    @return:  
    """
    x=0
    y=0
    z=0
    
    if sizeX == 0 and sizeY == 0 and sizeZ == 0:
        return [x,y,z] 
    
    if reducedToFull:
        x = sizeX
        y = sizeY 
        z = (sizeZ - 1)* 2
        
        if x == y and abs(z-y) == 1:
            #if x == y and x is odd, then z will be one pixel off. 
            #adjust accordingly that x == y == z
            z = y
            print('Warning: PyTom assumes that the shape of the real volume is :',x,y,z)
            print('Warning: Check if that is consistent with your data!')
            
    else:
        x = sizeX 
        y = sizeY 
        z = sizeZ / 2 + 1
    
    if x < 0 or y < 0 or z < 0:
        raise ValueError('fourierSizeOperation: Size determined is negative!')
    
    return [int(x),int(y),int(z)]

def powerspectrum(volume):
    """
    compute power spectrum of a volume
    
    @param volume: input volume
    @type volume: L{pytom_volume.vol}
    @return: power spectrum of vol
    @rtype: L{pytom_volume.vol}

    @author: FF
    """
    from pytom.basic.fourier import fft, ftshift
    from pytom_volume import vol
    from pytom_volume import reducedToFull

    fvol = ftshift(reducedToFull(fft(volume)),inplace=False)
    nx=fvol.sizeX()
    ny=fvol.sizeY()
    nz=fvol.sizeZ()
    ps = vol(nx,ny,nz)
    sf = 1./(nx*ny*nz)

    for ix in range(0,nx):
        for iy in range(0,ny):
            for iz in range(0,nz):
                temp = fvol.getV(ix,iy,iz)
                temp = temp*temp.conjugate()*sf
                ps.setV(float(temp.real),ix,iy,iz)
    return ps


