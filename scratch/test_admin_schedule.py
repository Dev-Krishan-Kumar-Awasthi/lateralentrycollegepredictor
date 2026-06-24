import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db
from college_meta import get_counselling_schedule

def test_schedule_updates():
    print("=== Testing Admin Counselling Schedule Update ===")
    
    with app.test_request_context():
        with app.test_client() as client:
            # 1. Login as admin
            print("Logging in as admin...")
            client.post('/account', data={
                'action': 'login',
                'email': 'krishnaawasthi701@gmail.com',
                'password': 'kkawasthi@202956@kka'
            }, follow_redirects=True)
            
            # 2. Get current schedule to preserve it
            orig_schedule = get_counselling_schedule()
            print(f"Original Academic Year: {orig_schedule.get('academic_year')}")
            
            # 3. Post updated schedule
            print("Posting schedule update...")
            test_year = "2026-27-TEST"
            post_data = {
                'academic_year': test_year,
                'portal_url': 'https://dte.mponline.gov.in',
                'event_id_0': 'registration',
                'event_title_0': 'Online Registration / Cancel Registration',
                'event_status_0': 'active',
                'event_date_0': '2026-06-20',
                'event_end_date_0': '2026-07-26',
                'event_time_desc_0': 'रात्रि 11:45 बजे तक',
                'event_description_0': 'Test Registration Desc'
            }
            
            resp = client.post('/admin/update-schedule', data=post_data, follow_redirects=True)
            print(f"POST /admin/update-schedule status code: {resp.status_code}")
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            
            # 4. Verify updated values on disk and in memory cache
            updated_schedule = get_counselling_schedule()
            print(f"Updated Academic Year: {updated_schedule.get('academic_year')}")
            assert updated_schedule.get('academic_year') == test_year, "Academic year did not update!"
            
            # Verify events
            events = updated_schedule.get('events', [])
            assert len(events) == 1, f"Expected 1 event, got {len(events)}"
            assert events[0]['id'] == 'registration'
            assert events[0]['status'] == 'active'
            assert events[0]['description'] == 'Test Registration Desc'
            
            # 5. Restore original schedule
            print("Restoring original schedule...")
            from college_meta import save_counselling_schedule
            save_counselling_schedule(orig_schedule)
            
            restored_schedule = get_counselling_schedule()
            print(f"Restored Academic Year: {restored_schedule.get('academic_year')}")
            assert restored_schedule.get('academic_year') == orig_schedule.get('academic_year'), "Schedule restore failed!"
            
            print("All schedule update verification assertions passed successfully!")

if __name__ == "__main__":
    test_schedule_updates()
