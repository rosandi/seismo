function fun(x,f,th,n) {
    x=6.28*x/n
    th=6.28*th/n
    s=f*x-th
    val=sin(s)*exp(-0.5*(x-th)^2/0.25)
    return val
}

BEGIN{
print "#$location -6.914864 107.608238"
print "#$time 2000"
print "#$ndata 100"
print "#$channels 0 1 2"
  for(i=0;i<=99;i++)
    print i,
    fun(i,10,0,100),
    fun(i,10,30,100),
    fun(i,10,60,100)
}
