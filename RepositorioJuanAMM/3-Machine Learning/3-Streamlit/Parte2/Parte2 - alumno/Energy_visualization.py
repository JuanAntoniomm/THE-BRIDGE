import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


def paint_distribution_categorical(df, categorical_columns, relative=False, show_values=False):
    num_columns = len(categorical_columns)
    num_rows = (num_columns // 2) + (num_columns % 2)

    fig, axes = plt.subplots(num_rows, 2, figsize=(15, 5 * num_rows))
    axes = axes.flatten() 

    for i, col in enumerate(categorical_columns):
        ax = axes[i]
        if relative:
            total = df[col].value_counts().sum()
            series = df[col].value_counts().apply(lambda x: x / total)
            sns.barplot(x=series.index, y=series, ax=ax, palette='viridis', hue = series.index, legend = False)
            ax.set_ylabel('Relative Frequency')
        else:
            series = df[col].value_counts()
            sns.barplot(x=series.index, y=series, ax=ax, palette='viridis', hue = series.index, legend = False)
            ax.set_ylabel('Frequency')

        ax.set_title(f'Distribution of {col}')
        ax.set_xlabel('')
        ax.tick_params(axis='x', rotation=45)

        if show_values:
            for p in ax.patches:
                height = p.get_height()
                ax.annotate(f'{height:.2f}', (p.get_x() + p.get_width() / 2., height), 
                            ha='center', va='center', xytext=(0, 9), textcoords='offset points')

    for j in range(i + 1, num_rows * 2):
        axes[j].axis('off')

    plt.tight_layout()
    plt.show()



def plot_categorical_relationship_end(df, cat_col1, cat_col2, relative_freq=False, show_values=False, size_group = 5):
    # Prepare the data
    count_data = df.groupby([cat_col1, cat_col2]).size().reset_index(name='count')
    total_counts = df[cat_col1].value_counts()
    
    # Convert to relative frequencies if requested
    if relative_freq:
        count_data['count'] = count_data.apply(lambda x: x['count'] / total_counts[x[cat_col1]], axis=1)

    # If there are more than size_group categories in cat_col1, divide them into groups of size_group.
    unique_categories = df[cat_col1].unique()
    if len(unique_categories) > size_group:
        num_plots = int(np.ceil(len(unique_categories) / size_group))

        for i in range(num_plots):
            # Select a subset of categories for each chart
            categories_subset = unique_categories[i * size_group:(i + 1) * size_group]
            data_subset = count_data[count_data[cat_col1].isin(categories_subset)]

            # Create the graph
            plt.figure(figsize=(10, 6))
            ax = sns.barplot(x=cat_col1, y='count', hue=cat_col2, data=data_subset, order=categories_subset)

            # Add titles and labels
            plt.title(f'Relationship between {cat_col1} and {cat_col2} - Group {i + 1}')
            plt.xlabel(cat_col1)
            plt.ylabel('Frequency' if relative_freq else 'Count')
            plt.xticks(rotation=45)

            # Display values on the chart
            if show_values:
                for p in ax.patches:
                    ax.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                                ha='center', va='center', fontsize=10, color='black', xytext=(0, size_group),
                                textcoords='offset points')

            # Display the graph
            plt.show()
    else:
        # Create the chart for fewer than size_group categories
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x=cat_col1, y='count', hue=cat_col2, data=count_data)

        # Add titles and labels
        plt.title(f'Relationship between {cat_col1} and {cat_col2}')
        plt.xlabel(cat_col1)
        plt.ylabel('Frequency' if relative_freq else 'Count')
        plt.xticks(rotation=45)

        # Display values on the chart
        if show_values:
            for p in ax.patches:
                ax.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='center', fontsize=10, color='black', xytext=(0, size_group),
                            textcoords='offset points')

        # Display the graph
        plt.show()



def plot_categorical_numerical_relationship(df, categorical_col, numerical_col, show_values=False, measure='mean'):
    # Calculate the measure of central tendency (mean or median).
    if measure == 'median':
        grouped_data = df.groupby(categorical_col)[numerical_col].median()
    else:
        # By default, use the average
        grouped_data = df.groupby(categorical_col)[numerical_col].mean()

    # Sort the values
    grouped_data = grouped_data.sort_values(ascending=False)

    # If there are more than 5 categories, divide them into groups of 5.
    if grouped_data.shape[0] > 5:
        unique_categories = grouped_data.index.unique()
        num_plots = int(np.ceil(len(unique_categories) / 5))

        for i in range(num_plots):
            # Select a subset of categories for each chart
            categories_subset = unique_categories[i * 5:(i + 1) * 5]
            data_subset = grouped_data.loc[categories_subset]

            # Create the graph
            plt.figure(figsize=(10, 6))
            ax = sns.barplot(x=data_subset.index, y=data_subset.values)

            # Add titles and labels
            plt.title(f'Relationship between {categorical_col} and {numerical_col} - Group {i + 1}')
            plt.xlabel(categorical_col)
            plt.ylabel(f'{measure.capitalize()} of {numerical_col}')
            plt.xticks(rotation=45)

            # Display values on the chart
            if show_values:
                for p in ax.patches:
                    ax.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                                ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                                textcoords='offset points')

            # Display the graph
            plt.show()
    else:
        # Create the chart for fewer than 5 categories
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x=grouped_data.index, y=grouped_data.values)

        # Add titles and labels
        plt.title(f'Relationship between {categorical_col} and {numerical_col}')
        plt.xlabel(categorical_col)
        plt.ylabel(f'{measure.capitalize()} of {numerical_col}')
        plt.xticks(rotation=45)

        # Display values on the chart
        if show_values:
            for p in ax.patches:
                ax.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                            textcoords='offset points')

        # Display the graph
        plt.show()


def plot_combined_graphs(df, columns, whisker_width=1.5, bins = None):
    num_cols = len(columns)
    if num_cols:
        
        fig, axes = plt.subplots(num_cols, 2, figsize=(12, 5 * num_cols))
        print(axes.shape)

        for i, column in enumerate(columns):
            if df[column].dtype in ['int64', 'float64']:
                # Histogram and KDE
                sns.histplot(df[column], kde=True, ax=axes[i,0] if num_cols > 1 else axes[0], bins= "auto" if not bins else bins)
                if num_cols > 1:
                    axes[i,0].set_title(f'Histogram and KDE of {column}')
                else:
                    axes[0].set_title(f'Histogram and KDE of {column}')

                # Boxplot
                sns.boxplot(x=df[column], ax=axes[i,1] if num_cols > 1 else axes[1], whis=whisker_width)
                if num_cols > 1:
                    axes[i,1].set_title(f'Boxplot of {column}')
                else:
                    axes[1].set_title(f'Boxplot of {column}')

        plt.tight_layout()
        plt.show()

def plot_grouped_boxplots(df, cat_col, num_col):
    unique_cats = df[cat_col].unique()
    num_cats = len(unique_cats)
    group_size = 5

    for i in range(0, num_cats, group_size):
        subset_cats = unique_cats[i:i+group_size]
        subset_df = df[df[cat_col].isin(subset_cats)]
        
        plt.figure(figsize=(10, 6))
        sns.boxplot(x=cat_col, y=num_col, data=subset_df)
        plt.title(f'Boxplots of {num_col} for {cat_col} (Group {i//group_size + 1})')
        plt.xticks(rotation=45)
        plt.show()



def plot_grouped_histograms(df, cat_col, num_col, group_size):
    unique_cats = df[cat_col].unique()
    num_cats = len(unique_cats)

    for i in range(0, num_cats, group_size):
        subset_cats = unique_cats[i:i+group_size]
        subset_df = df[df[cat_col].isin(subset_cats)]
        
        plt.figure(figsize=(10, 6))
        for cat in subset_cats:
            sns.histplot(subset_df[subset_df[cat_col] == cat][num_col], kde=True, label=str(cat))
        
        plt.title(f'Histograms of {num_col} for {cat_col} (Group {i//group_size + 1})')
        plt.xlabel(num_col)
        plt.ylabel('Frequency')
        plt.legend()
        plt.show()

####

def graph_dispersion_with_correlation(df, column_x, column_y, point_size=50, show_correlation=False):
    """
    Creates a scatter plot between two columns and optionally displays the correlation.

    Args:
    df (pandas.DataFrame): DataFrame containing the data.
    column_x (str): Name of the column for the X axis.
    column_y (str): Name of the column for the Y axis.
    dot_size (int, optional): Size of the dots in the graph. The default is 50.
    show_correlation (bool, optional): If True, show the correlation in the graph. The default is False.
    """

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x=column_x, y=column_y, s=point_size)

    if show_correlation:
        correlation = df[[column_x, column_y]].corr().iloc[0, 1]
        plt.title(f'Scatter Plot with Correlation: {correlation:.2f}')
    else:
        plt.title('Scatter Diagram')

    plt.xlabel(column_x)
    plt.ylabel(column_y)
    plt.grid(True)
    plt.show()


def bubble_plot(df, col_x, col_y, col_size, scale = 1000):
    """
    Create a scatter plot using two columns for the X and Y axes,
    and a third column to determine the size of the points.

    Args:
    df (pd.DataFrame): Pandas DataFrame.
    col_x (str): Name of the column for the X axis.
    col_y (str): Name of the column for the Y axis.
    col_size (str): Name of the column to determine the size of the points.
    """

    # Ensure that the size values are positive.
    sizes = (df[col_size] - df[col_size].min() + 1)/scale

    plt.scatter(df[col_x], df[col_y], s=sizes)
    plt.xlabel(col_x)
    plt.ylabel(col_y)
    plt.title(f'Bubbles of {col_x} vs {col_y} with Size based on {col_size}')
    plt.show()


