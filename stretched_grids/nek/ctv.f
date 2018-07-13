C-----------------------------------------------------------------------
C  nek5000 user-file template
C
C  user specified routines:
C     - userbc : boundary conditions
C     - useric : initial conditions
C     - uservp : variable properties
C     - userf  : local acceleration term for fluid
C     - userq  : local source term for scalars
C     - userchk: general purpose routine for checking errors etc.
C
C-----------------------------------------------------------------------
      subroutine uservp(ix,iy,iz,eg) ! set variable properties
      include 'SIZE'
      include 'TOTAL'
      include 'NEKUSE'

      integer e,f,eg
c     e = gllel(eg)

      udiff  = 0.0
      utrans = 0.0

      return
      end
c-----------------------------------------------------------------------
      subroutine userf(ix,iy,iz,eg) ! set acceleration term
c
c     Note: this is an acceleration term, NOT a force!
c     Thus, ffx will subsequently be multiplied by rho(x,t).
c
      include 'SIZE'
      include 'TOTAL'
      include 'NEKUSE'

      integer e,f,eg
c     e = gllel(eg)


      ffx=0.d0
      ffy=0.d0
      ffz=0.d0


      return
      end
c-----------------------------------------------------------------------
      subroutine userq(ix,iy,iz,eg) ! set source term
      include 'SIZE'
      include 'TOTAL'
      include 'NEKUSE'

      integer e,f,eg
c     e = gllel(eg)

      qvol   = 0.0
      source = 0.0

      return
      end
c-----------------------------------------------------------------------
      subroutine userbc(ix,iy,iz,f,eg) ! set up boundary conditions

c     NOTE: This routine may or may not be called by every processor

      include 'SIZE'
      include 'TOTAL'
      include 'NEKUSE'

      integer e,f,eg

      ux   = 0.0
      uy   = 0.0
      uz   = 0.0
      temp = 0.0

      return
      end
c-----------------------------------------------------------------------
      subroutine useric(ix,iy,iz,eg) ! set up initial conditions
      include 'SIZE'
      include 'TOTAL'
      include 'NEKUSE'
      integer e,eg

      real :: u0,v0

      pi  = acos(-1.)
       !pi  = 3.14159265

      u0=1.d0
      v0=1.d0

      ux   = u0 - cos(pi*x)*sin(pi*y)
      uy   = v0 + sin(pi*x)*cos(pi*y)
      uz   = 0.0
      temp = 0.0

      return
      end
c-----------------------------------------------------------------------
      subroutine userchk()
      include 'SIZE'
      include 'TOTAL'

      integer :: i,n
      real :: uerr(lx1,ly1,lz1,lelt)
      real :: verr(lx1,ly1,lz1,lelt)
      real :: u0,v0,g_uerr,g_verr
      real :: exact_u,exact_v,omega, mu

      pi=acos(-1.0)
      mu=param(2)
      omega = pi**2 * mu
      u0=1.d0
      v0=1.d0
      
      n = nx1 * ny1 * nz1 * nelt
      if (istep.eq.0) call outpost(vx,vy,vz,pr,t,'   ')

      if (istep.eq.0) write(42,*) "time uerror verror"

      if (mod(istep,1) == 0) then
	
	uerr=0.0
	verr=0.0
	do i=1,n
	  exact_u=u0 - cos(pi*(xm1(i,1,1,1)-u0*time))
     &                *sin(pi*(ym1(i,1,1,1)-v0*time))*
     &                exp(-2.0*omega*time)

	  exact_v=v0 + sin(pi*(xm1(i,1,1,1)-u0*time))
     &                *cos(pi*(ym1(i,1,1,1)-v0*time))*
     &                exp(-2.0*omega*time)

	uerr(i,1,1,1) = uerr(i,1,1,1)+(vx(i,1,1,1)-exact_u)**2
        verr(i,1,1,1) = verr(i,1,1,1)+(vy(i,1,1,1)-exact_v)**2
	enddo

	g_uerr=sqrt(glsum(uerr,n)/n)
        g_verr=sqrt(glsum(verr,n)/n)

	if(nid .eq. 0) then
		write(42,*) time, g_uerr, g_verr
	endif
      endif  
 
      return
      end
c-----------------------------------------------------------------------
      subroutine usrdat()   ! This routine to modify element vertices
      include 'SIZE'
      include 'TOTAL'

      return
      end
c-----------------------------------------------------------------------
      subroutine usrdat2()  ! This routine to modify mesh coordinates
      include 'SIZE'
      include 'TOTAL'

      return
      end
c-----------------------------------------------------------------------
      subroutine usrdat3()
      include 'SIZE'
      include 'TOTAL'

      return
      end
c-----------------------------------------------------------------------

c automatically added by makenek
      subroutine usrsetvert(glo_num,nel,nx,ny,nz) ! to modify glo_num
      integer*8 glo_num(1)

      return
      end

c automatically added by makenek
      subroutine userqtl

      call userqtl_scig

      return
      end
