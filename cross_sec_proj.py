import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Your data: Cm energies in TeV and corresponding cross sections (replace with your actual data)
energies = np.array([13.6, 60, 72, 80, 84, 100, 120])  # example energies
cross_sections = np.array([0.507, 17.38, 24.6, 29.90, 32.70, 44.55, 61.49])  # example cross sections

# Define the power law function
def power_law(E, A, n):
    return A * E**n

# Fit the data to the power law
params, covariance = curve_fit(power_law, energies, cross_sections)
A_fit, n_fit = params

print(f"Fitted parameters: A = {A_fit:.4e}, n = {n_fit:.4f}")

# Predict cross section at 50 TeV
E_pred = 50
cross_section_pred = power_law(E_pred, A_fit, n_fit)
print(f"Predicted cross section at {E_pred} TeV: {cross_section_pred:.4f}")

# Plotting
E_plot = np.linspace(min(energies)*0.9, max(energies)*1.1, 500)
sigma_plot = power_law(E_plot, A_fit, n_fit)

plt.figure(figsize=(8,6))
plt.scatter(energies, cross_sections, color='red', label='Data points')
plt.plot(E_plot, sigma_plot, label=f'Power law fit: $\\sigma = {A_fit:.2e} \\times E^{{{n_fit:.2f}}}$')
plt.scatter(E_pred, cross_section_pred, color='blue', label=f'Prediction at {E_pred} TeV')

plt.xlabel('Center-of-mass energy (TeV)')
plt.ylabel('Cross section (units)')
plt.title('Cross section of ttH01j vs Cm energy')
plt.legend()
plt.grid(True)

# Save plot as PDF
plt.savefig("ttH01j_cross_section_vs_energy.pdf")

plt.show()