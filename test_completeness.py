import matplotlib.pyplot as plt
import pandas as pd

from dominator_mutants import calculate_dominating_mutants, \
    convert_csv_to_killmap


def generate_test_completeness_plot(kill_map):
    """Generates the test completeness plot

    Takes a mapping of mutants to the tests that kill them.
    Calls calculate_dominating_mutants on the given kill_map to store a
    dominator set of mutants.

    get_tests_covered is called on each of the mutants in the dominator
    set to generate a mapping of each dominator mutant to the set of tests
    (mutant test set) that kill that mutant.

    For each point plotted (each iteration) the tests that are used in the
    plot (tests that kill the presented mutant) are subtracted from the
    remaining mutants' test set. That is, if test t_A kills mutants m1, m2,
    and m3, once we explore mutant m1 and count test t_A towards one plotted
    point, we can no longer count it for m2, and m3 in subsequent plotted
    points.

    After each iteration the remaining mutants are re-sorted based on the
    number of remaining tests that kill them.

    The above process is repeated until all dominating mutants are considered.

    Parameters:
        kill_map: A mapping from a set of identifiers from mutants killed to a
        set of identifiers for tests that kill each mutant.
    Returns:
        plot: List[tuple(int, int)]
            A list of plot points that could used to plot test completeness
    """

    # Get the dominator set of mutants and their graph
    result = calculate_dominating_mutants(kill_map)
    dominator_set = result[2]
    graph = result[0]
    plot = [(0, 0)]

    # Initialize a a dictionary to keep track of test completeness
    test_completeness_dict = dict()

    # Add dominator mutants and their covered tests to the list
    # Create a mapping of mutant -> {tests}
    for mutants in dominator_set:
        test_completeness_dict[mutants.mutant_identifier] = \
            graph.get_tests_covered(mutants)

    # Create a sorted list of dominator mutants based on the number of tests
    # they cover

    tests_added_plotted_so_far = set()

    # Add its tests so far to the list
    for mutants_counter in (range(len(test_completeness_dict.copy().items()))):
        # 1.3 generate new sorted list (resort list)
        sorted_list = sorted(test_completeness_dict,
                             key=lambda k: len(test_completeness_dict[k]),
                             reverse=True)

        # Add the tests from the latest mutant to the set of tests already
        # visited

        tests_added_plotted_so_far = tests_added_plotted_so_far.union(
            test_completeness_dict.get(
                sorted_list[0]))

        # Add new point to the plot using the x = muntants counter and
        # y = len(# tests) as

        plot.append((mutants_counter + 1, len(tests_added_plotted_so_far)))

        # Remove tests added so far from the rest of the list (DO need to
        # use a for loop inside this for loop for the rest of the mutants on the
        # list)

        for other_mutants in range(1, len(sorted_list)):
            temp = test_completeness_dict.get(sorted_list[other_mutants])
            temp = temp - tests_added_plotted_so_far
            test_completeness_dict[sorted_list[other_mutants]] = temp
        # Remove the current mutant from the dict
        test_completeness_dict.pop(sorted_list[0])

    return plot


def generate_test_completeness_plot_from_csv(csv_filename):
    """Generates the test completeness plot given a CSV file containing the
    mapping from mutants to tests that kill those mutants

    See documentation for convert_csv_to_killmap,
    generate_test_completeness_plot, and plot

    Parameters:
        csv_filename: .csv document
            A csv document generated by the Major framework containing a
            mapping from mutants to the tests they kill
    Returns:
        plotted_points: List[tuple(int, int)]
            A list of plot points that could used to plot test completeness
    """
    kill_map = convert_csv_to_killmap(csv_filename)
    plotted_points = generate_test_completeness_plot(kill_map)

    # todo: update the spec to include this return value
    plots = plot(plotted_points)
    return plotted_points, plots


def plot(plot):
    """Plots the test completeness graph


    Parameters:
         plot: List[tuple(int, int)]
            A list of plot points that could used to plot test completeness
            """
    plotter = pd.DataFrame(
        data=plot,
        columns=["Work", "Test Completeness"]
    )
    ax = plotter.plot(x='Work', y='Dominator Mutants', fontsize=6,
                      xticks=(range(0, len(plot), 5)),
                      yticks=range(0, plot[(len(plot) - 1)][1], 25),
                      legend=False)
    ax.set_ylabel("Test Completeness")
    # plt.savefig("images/111.png")
    # plt.show()

    return plt
