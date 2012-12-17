function angle= Features_Compute(A,B,C)
x1=B(1,1)-A(1,1);
y1=B(1,2)-A(1,2);
z1=B(1,3)-A(1,3);
AB=[x1,y1,z1];
 
x2=C(1,1)-B(1,1);
y2=C(1,2)-B(1,2);
z2=C(1,3)-B(1,3);
BC=[x2,y2,z2];
 
lengthAB = sqrt(((AB(1,1))^2)+((AB(1,2))^2)+((AB(1,3))^2));
lengthBC = sqrt(((BC(1,1))^2)+((BC(1,2))^2)+((BC(1,3))^2));

unitvectorAB=[AB(1,1)/lengthAB, AB(1,2)/lengthAB, AB(1,3)/lengthAB];
unitvectorBC=[BC(1,1)/lengthBC, BC(1,2)/lengthBC, BC(1,3)/lengthBC];

costheta = (unitvectorAB(1,1)*unitvectorBC(1,1))+(unitvectorAB(1,2)*unitvectorBC(1,2))+(unitvectorAB(1,3)*unitvectorBC(1,3));
% The last one gives the angle in degrees from the 3D function:
 angle = radtodeg(acos(costheta)) %#ok<NOPRT>