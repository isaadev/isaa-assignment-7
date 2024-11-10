from flask import Flask, render_template, request, url_for, session
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from scipy.stats import t

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Replace with your own secret key, needed for session management


def generate_data(N, mu, beta0, beta1, sigma2, S):
    # Generate data and initial plots

    # TODO 1: Generate a random dataset X of size N with values between 0 and 1
    X = np.random.uniform(0,1, N)
    X_reshaped = X.reshape(-1,1)  # Replace with code to generate random values for X

    # TODO 2: Generate a random dataset Y using the specified beta0, beta1, mu, and sigma2
    # Y = beta0 + beta1 * X + mu + error term
    error = np.random.normal(0, np.sqrt(sigma2), N)
    Y = beta0 + beta1 * X + mu + error  # Replace with code to generate Y
    
    # TODO 3: Fit a linear regression model to X and Y
    model = LinearRegression()  # Initialize the LinearRegression model
    model.fit(X_reshaped, Y)# Fit the model to X and Y
    
    slope = model.coef_[0]  # Extract the slope (coefficient) from the fitted model
    intercept = model.intercept_  # Extract the intercept from the fitted model

    # TODO 4: Generate a scatter plot of (X, Y) with the fitted regression line
    plot1_path = "static/plot1.png"
    # Replace with code to generate and save the scatter plot
    plt.figure()
    plt.scatter(X, Y, label='Data')
    plt.plot(X, model.predict(X.reshape(-1, 1)), color='red', label='Fitted Line')
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.title("Generated Data with Fitted Regression Line")
    plt.savefig(plot1_path)
    plt.close()

    # TODO 5: Run S simulations to generate slopes and intercepts
    slopes = []
    intercepts = []

    for _ in range(S):
        # TODO 6: Generate simulated datasets using the same beta0 and beta1
        X_sim = np.random.uniform(0,1, N)  # Replace with code to generate simulated X values
        Y_sim = beta0 + beta1 * X_sim + np.random.normal(0, np.sqrt(sigma2), N)   # Replace with code to generate simulated Y values
        X_sim_reshaped = X_sim.reshape(-1,1)
        # TODO 7: Fit linear regression to simulated data and store slope and intercept
        sim_model = LinearRegression() # Replace with code to fit the model
        sim_model.fit(X_sim_reshaped, Y_sim)
        sim_slope = sim_model.coef_[0]  # Extract slope from sim_model

        sim_intercept = sim_model.intercept_  # Extract intercept from sim_model

        slopes.append(sim_slope)
        intercepts.append(sim_intercept)

    # TODO 8: Plot histograms of slopes and intercepts
    plot2_path = "static/plot2.png"
    # Replace with code to generate and save the histogram plot
    plt.figure()
    plt.hist(slopes, bins=30, alpha=0.7, label='Simulated Slopes')
    plt.hist(intercepts, bins=30, alpha=0.7, label='Simulated Intercepts')
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.legend()
    plt.title("Histogram of Simulated Slopes and Intercepts")
    plt.savefig(plot2_path)
    plt.close()
    


    # TODO 9: Return data needed for further analysis, including slopes and intercepts
    # Calculate proportions of slopes and intercepts more extreme than observed
    slope_more_extreme =  np.mean(np.abs(np.array(slopes) - beta1) >= np.abs(slope - beta1)) # Replace with code to calculate proportion of slopes more extreme than observed
    intercept_extreme = np.mean(np.abs(np.array(intercepts) - beta0) >= np.abs(intercept - beta0))  # Replace with code to calculate proportion of intercepts more extreme than observed

    # Return data needed for further analysis
    return (
        X,
        Y,
        slope,
        intercept,
        plot1_path,
        plot2_path,
        slope_more_extreme,
        intercept_extreme,
        slopes,
        intercepts,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get user input from the form
        N = int(request.form["N"])
        mu = float(request.form["mu"])
        sigma2 = float(request.form["sigma2"])
        beta0 = float(request.form["beta0"])
        beta1 = float(request.form["beta1"])
        S = int(request.form["S"])

        # Generate data and initial plots
        (
            X,
            Y,
            slope,
            intercept,
            plot1,
            plot2,
            slope_extreme,
            intercept_extreme,
            slopes,
            intercepts,
        ) = generate_data(N, mu, beta0, beta1, sigma2, S)

        # Store data in session
        session["X"] = X.tolist()
        session["Y"] = Y.tolist()
        session["slope"] = slope
        session["intercept"] = intercept
        session["slopes"] = slopes
        session["intercepts"] = intercepts
        session["slope_extreme"] = slope_extreme
        session["intercept_extreme"] = intercept_extreme
        session["N"] = N
        session["mu"] = mu
        session["sigma2"] = sigma2
        session["beta0"] = beta0
        session["beta1"] = beta1
        session["S"] = S

        # Return render_template with variables
        return render_template(
            "index.html",
            plot1=plot1,
            plot2=plot2,
            slope_extreme=slope_extreme,
            intercept_extreme=intercept_extreme,
            N=N,
            mu=mu,
            sigma2=sigma2,
            beta0=beta0,
            beta1=beta1,
            S=S,
        )
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    # This route handles data generation (same as above)
    return index()


@app.route("/hypothesis_test", methods=["POST"])
def hypothesis_test():
    # Retrieve data from session
    N = int(session.get("N"))
    if N is None:
        return "Error: Required session data not found. Please generate data first.", 400
    S = int(session.get("S"))
    slope = float(session.get("slope"))
    intercept = float(session.get("intercept"))
    slopes = session.get("slopes")
    intercepts = session.get("intercepts")
    beta0 = float(session.get("beta0"))
    beta1 = float(session.get("beta1"))

    parameter = request.form.get("parameter")
    test_type = request.form.get("test_type")

    # Use the slopes or intercepts from the simulations
    if parameter == "slope":
        simulated_stats = np.array(slopes)
        observed_stat = slope
        hypothesized_value = beta1
    else:
        simulated_stats = np.array(intercepts)
        observed_stat = intercept
        hypothesized_value = beta0

    # TODO 10: Calculate p-value based on test type
    p_value = None
    if test_type == ">":
        p_value = np.mean(simulated_stats > observed_stat)
    elif test_type == "<":
        p_value = np.mean(simulated_stats < observed_stat)
    else:  # not equal
        p_value = 2 * np.mean([abs(sim - hypothesized_value) >= abs(observed_stat - hypothesized_value) for sim in simulated_stats])

    # TODO 11: If p_value is very small (e.g., <= 0.0001), set fun_message to a fun message
    fun_message = "How pathetic. Small p-value." if p_value <= 0.0001 else None

    # TODO 12: Plot histogram of simulated statistics
    plot3_path = "static/plot3.png"
    # Replace with code to generate and save the plot
    plt.figure()
    plt.hist(simulated_stats, bins=30, alpha=0.7, label='Simulated Stats')
    plt.axvline(observed_stat, color='red', linestyle='--', label='Observed Stat')
    plt.axvline(hypothesized_value, color='blue', linestyle='--', label='Hypothesized Value')
    plt.xlabel("Statistic Value")
    plt.ylabel("Frequency")
    plt.legend()
    plt.title("Histogram of Simulated Statistics")
    plt.savefig(plot3_path)
    plt.close()

    # Return results to template
    return render_template(
        "index.html",
        plot1="static/plot1.png",
        plot2="static/plot2.png",
        plot3=plot3_path,
        parameter=parameter,
        observed_stat=observed_stat,
        hypothesized_value=hypothesized_value,
        N=N,
        beta0=beta0,
        beta1=beta1,
        S=S,
        # TODO 13: Uncomment the following lines when implemented
        p_value=p_value,
        fun_message=fun_message,
    )

@app.route("/confidence_interval", methods=["POST"])
def confidence_interval():
    # Retrieve data from session
    N = int(session.get("N"))
    if N is None:
        return "Error: Required session data not found. Please generate data first.", 400
    
    mu = float(session.get("mu"))
    sigma2 = float(session.get("sigma2"))
    beta0 = float(session.get("beta0"))
    beta1 = float(session.get("beta1"))
    S = int(session.get("S"))
    if S <= 1:
        return "Error: Number of simulations (S) must be greater than 1 to calculate a confidence interval.", 400
    
    X = np.array(session.get("X"))
    Y = np.array(session.get("Y"))
    slope = float(session.get("slope"))
    intercept = float(session.get("intercept"))
    slopes = session.get("slopes")
    intercepts = session.get("intercepts")

    parameter = request.form.get("parameter")
    confidence_level = float(request.form.get("confidence_level"))
    
    # Convert confidence level to a proportion if it's greater than 1
    if confidence_level > 1:
        confidence_level /= 100.0

    # Check if confidence level is between 0 and 1
    if not (0 < confidence_level < 1):
        return "Error: Confidence level must be between 0 and 1.", 400

    # Use the slopes or intercepts from the simulations
    if parameter == "slope":
        estimates = np.array(slopes)
        observed_stat = slope
        true_param = beta1
    else:
        estimates = np.array(intercepts)
        observed_stat = intercept
        true_param = beta0

    # Calculate mean and standard deviation of the estimates
    mean_estimate = np.mean(estimates)
    std_estimate = np.std(estimates, ddof=1) 
    if std_estimate == 0:
        std_estimate = 1e-10  # Small constant to avoid zero standard error

    # Calculate the t-value for the confidence interval
    tval = t.ppf(1 - (1 - confidence_level) / 2, df=S - 1)
    if np.isnan(tval):
        return "Error: Invalid t-value calculation. Check degrees of freedom and confidence level.", 400

    # Calculate confidence interval for the parameter estimate
    ci_lower = mean_estimate - tval * (std_estimate / np.sqrt(len(estimates)))
    ci_upper = mean_estimate + tval * (std_estimate / np.sqrt(len(estimates)))


    # Check if confidence interval includes true parameter
    includes_true = ci_lower <= true_param <= ci_upper

    # Plot the individual estimates as gray points and confidence interval
    plot4_path = "static/plot4.png"
    plt.figure(figsize=(8, 6))

    # Scatter plot of individual simulated estimates
    plt.scatter(estimates, [0] * len(estimates), color='gray', alpha=0.5, label='Simulated Estimates')

    # Plot the mean estimate as a large blue dot
    plt.plot(mean_estimate, 0, 'bo', markersize=10, label='Mean Estimate')

    # Plot the confidence interval as a horizontal line
    plt.hlines(y=0, xmin=ci_lower, xmax=ci_upper, color='purple', linestyle='-', linewidth=3, label=f'{confidence_level * 100}% Confidence Interval')

    # Plot the true parameter as a vertical dashed line
    plt.axvline(x=true_param, color='green', linestyle='--', linewidth=2, label='True Slope')

    # Labels and legend
    plt.xlabel("Slope Estimate")
    plt.ylabel("Density")
    plt.yticks([])  # Remove y-axis ticks for a cleaner look
    plt.legend()
    plt.title(f"{confidence_level * 100}% Confidence Interval for Slope (Mean Estimate)")

    
    
    plt.savefig(plot4_path)
    plt.close()

    # Return results to template
    return render_template(
        "index.html",
        plot1="static/plot1.png",
        plot2="static/plot2.png",
        plot4=plot4_path,
        parameter=parameter,
        confidence_level=confidence_level,
        mean_estimate=mean_estimate,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        includes_true=includes_true,
        observed_stat=observed_stat,
        N=N,
        mu=mu,
        sigma2=sigma2,
        beta0=beta0,
        beta1=beta1,
        S=S,
    )



if __name__ == "__main__":
    app.run(debug=True)
