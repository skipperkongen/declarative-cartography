import matplotlib.pyplot as plt
x = range(6)
plt.plot(x, [xi**2 for xi in x])
plt.plot(x, [xi**3 for xi in x])
plt.show()