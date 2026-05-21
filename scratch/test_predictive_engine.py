import os
import sys

# Add root folder to sys.path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from college_meta import get_placement_info, get_college_info_bundle

def test_engine():
    print("=== Testing Placement Predictive Engine ===")
    
    # 1. Test Seeded College (SGSITS)
    sgsits_name = "Shri G.S. Institute of Technology & Science, Indore (M.P.) (1952)"
    sgsits_info = get_placement_info(sgsits_name)
    print(f"\nSeeded College: {sgsits_name}")
    print(f"Average Package: {sgsits_info['average_package_lpa']} LPA")
    print(f"Highest Package: {sgsits_info['highest_package_lpa']} LPA")
    print(f"Placement %: {sgsits_info['placement_percentage']}%")
    print(f"Recruiters: {sgsits_info['top_recruiters']}")
    print(f"Is Predicted: {sgsits_info.get('is_predicted')}")
    assert sgsits_info['is_predicted'] is False, "SGSITS should use seeded data!"
    
    # 2. Test Unseeded Government College in Indore
    govt_college = "Institute of Technology - Government College, Indore"
    govt_info = get_placement_info(govt_college, "GOVT")
    print(f"\nUnseeded Government (Indore): {govt_college}")
    print(f"Average Package: {govt_info['average_package_lpa']} LPA")
    print(f"Highest Package: {govt_info['highest_package_lpa']} LPA")
    print(f"Placement %: {govt_info['placement_percentage']}%")
    print(f"Is Predicted: {govt_info.get('is_predicted')}")
    assert govt_info['is_predicted'] is True, "Unseeded college must be predicted!"
    
    # 3. Test Unseeded Private College
    private_college = "Random Private Institute of Engineering, Dewas"
    private_info = get_placement_info(private_college, "Private")
    print(f"\nUnseeded Private (Dewas): {private_college}")
    print(f"Average Package: {private_info['average_package_lpa']} LPA")
    print(f"Highest Package: {private_info['highest_package_lpa']} LPA")
    print(f"Placement %: {private_info['placement_percentage']}%")
    print(f"Is Predicted: {private_info.get('is_predicted')}")
    assert private_info['is_predicted'] is True
    
    print("\nAll predictive engine tests passed successfully!")

if __name__ == "__main__":
    test_engine()
